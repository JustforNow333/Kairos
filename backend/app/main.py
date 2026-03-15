from __future__ import annotations

import os
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .db import (
    DEMO_USER_ID, 
    initialize_database, 
    load_demo_snapshot, 
    replace_assignments, 
    update_user_assumptions, 
    upsert_user,
    get_user_assumptions,
    get_user_schedule,
    get_user_assignments,
    get_user_friends,
    get_user_tokens,
    save_schedule_blocks
)
from .schemas import DashboardResponse, IdleAlertRequest, ShuffleRequest, SocialPocketRequest, UserAssumptions
from .services.parser import parse_syllabus
from .services.weather import fetch_live_weather
from .services.fateweaver import build_fateweaver_tactics
from .services.scheduler import (
    build_idle_alert,
    build_shuffle_plan,
    build_social_readiness,
    build_work_debt_ledger,
    find_social_pockets,
)
from .services.google_calendar import fetch_google_calendar_events
from .auth import oauth


app = FastAPI(title="KAIROS Engine", version="0.1.0")

# Add SessionMiddleware (required by authlib for state verification)
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)


def parse_allowed_origins() -> list[str]:
    raw_origins = os.getenv("API_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["http://localhost:3000", "http://127.0.0.1:3000"]


ALLOWED_ORIGINS = parse_allowed_origins()
ALLOWED_ORIGIN_REGEX = os.getenv("API_ALLOWED_ORIGIN_REGEX")
ALLOW_CREDENTIALS = "*" not in ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=ALLOWED_ORIGIN_REGEX,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/dashboard/overview", response_model=DashboardResponse)
def dashboard_overview(request: Request) -> DashboardResponse:
    user_id = request.session.get("user_id", DEMO_USER_ID)
    
    assumptions = get_user_assumptions(user_id)
    course, assignments = get_user_assignments(user_id)
    friends = get_user_friends(user_id)
    current_schedule = get_user_schedule(user_id)
    
    _, _, _, _, _, idle_event, weather = load_demo_snapshot() # Mock for these contextual signals
    
    # If a new user logs in and has no data, temporarily inject the demo schedule so the app doesn't look broken
    if not current_schedule and user_id != DEMO_USER_ID:
        _, course, assignments, friends, current_schedule, _, _ = load_demo_snapshot()

    if not settings.USE_MOCK_DATA:
        weather = fetch_live_weather()
        
    pockets = find_social_pockets(friends, weather)
    ledger = build_work_debt_ledger(assignments, assumptions)
    social_readiness = build_social_readiness(current_schedule, pockets, assumptions)
    shuffle_plan = build_shuffle_plan(current_schedule, pockets)
    target_pocket = next((pocket for pocket in pockets if pocket.id == shuffle_plan.target_pocket_id), None)
    tactics, strategy_source = build_fateweaver_tactics(assignments, shuffle_plan, target_pocket)
    shuffle_plan = shuffle_plan.model_copy(update={"tactics": tactics, "strategy_source": strategy_source})
    idle_alert = build_idle_alert(idle_event=idle_event, pockets=pockets, assumptions=assumptions, social_readiness=social_readiness)

    return DashboardResponse(
        generated_at=datetime.now(),
        tagline="Live the life you planned, not the one you fell into.",
        assumptions=assumptions,
        weather=weather,
        course=course,
        assignments=assignments,
        ledger=ledger,
        social_readiness=social_readiness,
        friends=friends,
        pockets=pockets,
        current_schedule=current_schedule,
        shuffle_plan=shuffle_plan,
        idle_alert=idle_alert,
    )


@app.post("/api/v1/syllabus/parse")
async def syllabus_parse(file: UploadFile = File(...)):
    response = parse_syllabus(filename=file.filename, file_bytes=await file.read())
    replace_assignments(DEMO_USER_ID, response.course, response.assignments)
    return response


@app.post("/api/v1/social/pockets")
def social_pockets(request: SocialPocketRequest):
    _, _, _, _, _, _, weather = load_demo_snapshot()
    if not settings.USE_MOCK_DATA:
        weather = fetch_live_weather()
    return find_social_pockets(request.friends, weather)


@app.put("/api/v1/user/assumptions")
def update_assumptions(assumptions: UserAssumptions):
    update_user_assumptions(DEMO_USER_ID, assumptions)
    return {"status": "success"}


@app.get("/api/v1/auth/google/login")
async def google_login(request: Request):
    redirect_uri = str(request.url_for("google_auth_callback"))
    return await oauth.google.authorize_redirect(request, redirect_uri, access_type="offline", prompt="consent")

@app.get("/api/auth/callback")
async def google_auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")
    if userinfo:
        user_id = userinfo.sub
        name = userinfo.name
        email = userinfo.email
        access_token = token.get("access_token")
        refresh_token = token.get("refresh_token")
        expires_at = token.get("expires_at")
        
        token_expiry_iso = datetime.fromtimestamp(expires_at).isoformat() if expires_at else None

        upsert_user(
            user_id=user_id,
            name=name,
            email=email,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expiry=token_expiry_iso,
        )
        
        # Set session
        request.session['user_id'] = user_id
        
    return RedirectResponse(url=settings.NEXT_PUBLIC_APP_URL)


@app.get("/api/v1/user/sync-calendar")
def sync_calendar(request: Request):
    user_id = request.session.get("user_id", DEMO_USER_ID)
    
    # If using mock data or no credentials, load the demo schedule
    if settings.USE_MOCK_DATA or not settings.GOOGLE_CLIENT_ID or user_id == DEMO_USER_ID:
        _, _, _, _, schedule, _, _ = load_demo_snapshot()
        return {"status": "success", "blocks_synced": len(schedule), "mode": "mock"}
        
    # User is truly authenticated; fetch their live tokens
    tokens = get_user_tokens(user_id)
    if not tokens:
        return {"status": "error", "message": "No Google tokens found. Please connect your calendar."}
        
    try:
        blocks = fetch_google_calendar_events(
            access_token=tokens["google_access_token"],
            refresh_token=tokens["google_refresh_token"],
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET
        )
        save_schedule_blocks(user_id, blocks)
        return {"status": "success", "blocks_synced": len(blocks), "mode": "live"}
    except Exception as e:
        print(f"Failed to sync calendar: {e}")
        return {"status": "error", "message": "Failed to sync with Google Calendar."}


@app.post("/api/v1/shuffle/plan")
def shuffle_plan(request: ShuffleRequest):
    plan = build_shuffle_plan(request.schedule, request.pockets)
    target_pocket = next((pocket for pocket in request.pockets if pocket.id == plan.target_pocket_id), None)
    tactics, strategy_source = build_fateweaver_tactics([], plan, target_pocket)
    return plan.model_copy(update={"tactics": tactics, "strategy_source": strategy_source})


@app.post("/api/v1/idle")
def process_idle_event(idle_event: IdleEvent):
    assumptions, _, _, friends, schedule, _, weather = load_demo_snapshot()
    if not settings.USE_MOCK_DATA:
        weather = fetch_live_weather()
    pockets = find_social_pockets(friends, weather)
    if not pockets:
        return {"status": "no_action_needed"}
    readiness = build_social_readiness(schedule, pockets, assumptions)
    
    # Check if the distraction duration is long enough to trigger an alert
    if idle_event.duration_minutes >= 3:
        alert = build_idle_alert(idle_event, pockets, assumptions, readiness)
        return alert.model_dump()
        
    return {"status": "no_action_needed"}


@app.post("/api/v1/interventions/idle-alert")
def idle_alert(request: IdleAlertRequest):
    assumptions, _, _, _, current_schedule, _, _ = load_demo_snapshot()
    social_readiness = build_social_readiness(current_schedule, request.pockets, assumptions)
    return build_idle_alert(request.idle_event, request.pockets, assumptions, social_readiness)

class NewFriend(BaseModel):
    friend_name: str
    home_zone: str

@app.get("/api/v1/friends")
def get_friends():
    _, _, _, friends, _, _, _ = load_demo_snapshot()
    return friends

from .db import get_connection
@app.post("/api/v1/friends")
def add_friend(new_friend: NewFriend):
    with get_connection() as connection:
        friend_id = f"f-{new_friend.friend_name.lower().replace(' ', '')}"
        connection.execute(
            "INSERT INTO friends (id, user_id, friend_name, home_zone) VALUES (?, ?, ?, ?)",
            (friend_id, DEMO_USER_ID, new_friend.friend_name, new_friend.home_zone)
        )
    return {"status": "success", "friend_id": friend_id}
