from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .db import initialize_database, load_demo_snapshot, replace_assignments
from .schemas import DashboardResponse, IdleAlertRequest, ShuffleRequest, SocialPocketRequest
from .services.parser import parse_syllabus
from .services.scheduler import (
    build_idle_alert,
    build_shuffle_plan,
    build_social_readiness,
    build_work_debt_ledger,
    find_social_pockets,
)


app = FastAPI(title="KAIROS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
def dashboard_overview() -> DashboardResponse:
    assumptions, course, assignments, friends, current_schedule, idle_event, weather = load_demo_snapshot()
    pockets = find_social_pockets(friends, weather)
    ledger = build_work_debt_ledger(assignments, assumptions)
    social_readiness = build_social_readiness(current_schedule, pockets, assumptions)
    shuffle_plan = build_shuffle_plan(current_schedule, pockets)
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
    replace_assignments(response.course, response.assignments)
    return response


@app.post("/api/v1/social/pockets")
def social_pockets(request: SocialPocketRequest):
    _, _, _, _, _, _, weather = load_demo_snapshot()
    return find_social_pockets(request.friends, weather)


@app.post("/api/v1/shuffle/plan")
def shuffle_plan(request: ShuffleRequest):
    return build_shuffle_plan(request.schedule, request.pockets)


@app.post("/api/v1/interventions/idle-alert")
def idle_alert(request: IdleAlertRequest):
    assumptions, _, _, _, current_schedule, _, _ = load_demo_snapshot()
    social_readiness = build_social_readiness(current_schedule, request.pockets, assumptions)
    return build_idle_alert(request.idle_event, request.pockets, assumptions, social_readiness)
