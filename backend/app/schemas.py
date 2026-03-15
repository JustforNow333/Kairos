from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UserAssumptions(BaseModel):
    reading_speed_pph: int = 28
    major_difficulty_multiplier: float = 1.1
    historical_productivity_multiplier: float = 0.95
    social_readiness_goal_hours: float = 6.0


class WeatherContext(BaseModel):
    summary: str
    condition: str
    temperature_f: int


class Course(BaseModel):
    code: str
    title: str


class Assignment(BaseModel):
    id: str
    course_code: str
    title: str
    task_type: Literal["pset", "reading", "essay", "lab", "exam_prep"]
    due_at: datetime
    base_effort_hours: float
    estimated_weight: int = Field(ge=1, le=5)
    reading_pages: int = 0
    status: Literal["pending", "in_progress", "done"] = "pending"


class WorkDebtItem(BaseModel):
    assignment_id: str
    title: str
    adjusted_effort_hours: float
    interest_multiplier: float
    debt_contribution: float
    due_at: datetime


class WorkDebtLedger(BaseModel):
    work_debt_score: float
    total_hours: float
    interest_drag_hours: float
    focus_hours_today: float
    summary: str
    items: list[WorkDebtItem]


class AvailabilityWindow(BaseModel):
    start_at: datetime
    end_at: datetime
    location_hint: str


class FriendAvailability(BaseModel):
    friend_id: str
    friend_name: str
    windows: list[AvailabilityWindow]


class SocialPocket(BaseModel):
    id: str
    start_at: datetime
    end_at: datetime
    title: str
    location_hint: str
    friend_names: list[str]
    score: float
    claimability: str
    why_now: str
    activity_suggestion: str
    day_phase: str
    weather_label: str
    emotional_hook: str


class ScheduleBlock(BaseModel):
    id: str
    label: str
    block_type: Literal["class", "work", "social", "buffer", "meal"]
    start_at: datetime
    end_at: datetime
    movable: bool
    intensity: float = 1.0


class ShufflePlan(BaseModel):
    before_blocks: list[ScheduleBlock]
    after_blocks: list[ScheduleBlock]
    target_pocket_id: str
    tradeoff_statement: str
    focus_boost_multiplier: float
    unlocked_minutes: int
    tactics: list[str] = []
    strategy_source: str = "rule-based"


class IdleEvent(BaseModel):
    source: Literal["mocked_browser_feed", "chrome_extension"]
    app_name: str
    duration_minutes: int
    detected_at: datetime


class IdleAlert(BaseModel):
    headline: str
    action: str
    social_readiness_gap_hours: float
    friend_names: list[str]
    target_pocket_id: str


class SocialReadiness(BaseModel):
    score: float
    weekly_target_hours: float
    projected_hours: float
    gap_hours: float
    status: str
    summary: str


class DashboardResponse(BaseModel):
    generated_at: datetime
    tagline: str
    assumptions: UserAssumptions
    weather: WeatherContext
    course: Course
    assignments: list[Assignment]
    ledger: WorkDebtLedger
    social_readiness: SocialReadiness
    friends: list[FriendAvailability]
    pockets: list[SocialPocket]
    current_schedule: list[ScheduleBlock]
    shuffle_plan: ShufflePlan
    idle_alert: IdleAlert


class SyllabusParseResponse(BaseModel):
    course: Course
    assignments: list[Assignment]
    ledger: WorkDebtLedger
    parser_mode: str
    notes: str


class SocialPocketRequest(BaseModel):
    friends: list[FriendAvailability]


class ShuffleRequest(BaseModel):
    schedule: list[ScheduleBlock]
    pockets: list[SocialPocket]


class IdleAlertRequest(BaseModel):
    idle_event: IdleEvent
    pockets: list[SocialPocket]
