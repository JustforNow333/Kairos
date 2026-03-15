from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

import httpx
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from ..schemas import ScheduleBlock

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

def fetch_google_calendar_events(access_token: str, refresh_token: str | None, client_id: str, client_secret: str) -> list[ScheduleBlock]:
    """
    Fetches events from the user's primary Google Calendar for the next 7 days
    and maps them into KAIROS ScheduleBlock items.
    """
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )
    
    service = build("calendar", "v3", credentials=creds)
    
    now = datetime.utcnow().isoformat() + "Z"
    next_week = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
    
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            timeMax=next_week,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    
    blocks: list[ScheduleBlock] = []
    
    for event in events:
        start_str = event["start"].get("dateTime")
        end_str = event["end"].get("dateTime")
        
        # Skip all-day events for now (they only have 'date', not 'dateTime')
        if not start_str or not end_str:
            continue
            
        start_at = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        end_at = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        
        summary = event.get("summary", "Busy")
        
        # Determine block type heuristically
        lower_summary = summary.lower()
        if any(keyword in lower_summary for keyword in ["class", "lecture", "seminar", "discussion"]):
            block_type = "class"
        elif any(keyword in lower_summary for keyword in ["lunch", "dinner", "breakfast", "meal"]):
            block_type = "meal"
        else:
            block_type = "work" # default imported blocks to work/busy
            
        blocks.append(
            ScheduleBlock(
                id=event["id"],
                label=summary,
                block_type=block_type,
                start_at=start_at,
                end_at=end_at,
                movable=False, # Imported calendar events are strictly fixed
                intensity=1.0,
            )
        )
        
    return blocks
