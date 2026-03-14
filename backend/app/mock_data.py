from __future__ import annotations

from datetime import datetime, timedelta

from .schemas import (
    Assignment,
    AvailabilityWindow,
    Course,
    FriendAvailability,
    IdleEvent,
    ScheduleBlock,
    UserAssumptions,
    WeatherContext,
)


def _today_at(hour: int, minute: int = 0) -> datetime:
    now = datetime.now().replace(second=0, microsecond=0)
    return now.replace(hour=hour, minute=minute)


def default_assumptions() -> UserAssumptions:
    return UserAssumptions(
        reading_speed_pph=26,
        major_difficulty_multiplier=1.15,
        historical_productivity_multiplier=0.92,
        social_readiness_goal_hours=7.0,
    )


def default_user_profile() -> dict[str, str | int | float]:
    return {
        "name": "Avery Chen",
        "email": "avery@cornell.edu",
        "major": "Computer Science",
        "reading_speed_pph": 26,
        "major_difficulty_multiplier": 1.15,
        "historical_productivity_multiplier": 0.92,
        "social_readiness_goal_hours": 7.0,
    }


def default_course() -> Course:
    return Course(code="CS 3110", title="Data Structures and Functional Programming")


def default_assignments() -> list[Assignment]:
    return [
        Assignment(
            id="a1",
            course_code="CS 3110",
            title="Problem Set 4",
            task_type="pset",
            due_at=_today_at(23, 0) + timedelta(days=1),
            base_effort_hours=6.5,
            estimated_weight=5,
        ),
        Assignment(
            id="a2",
            course_code="ECON 1110",
            title="Behavioral Econ Reading",
            task_type="reading",
            due_at=_today_at(18, 30) + timedelta(days=2),
            base_effort_hours=1.5,
            estimated_weight=2,
            reading_pages=42,
        ),
        Assignment(
            id="a3",
            course_code="INFO 1300",
            title="Studio Critique Prep",
            task_type="essay",
            due_at=_today_at(10, 0) + timedelta(days=3),
            base_effort_hours=3.5,
            estimated_weight=3,
        ),
        Assignment(
            id="a4",
            course_code="MATH 1920",
            title="Oscillation Review Set",
            task_type="exam_prep",
            due_at=_today_at(20, 0) + timedelta(days=4),
            base_effort_hours=4.0,
            estimated_weight=4,
        ),
    ]


def default_friend_availability() -> list[FriendAvailability]:
    return [
        FriendAvailability(
            friend_id="f1",
            friend_name="Maya",
            windows=[
                AvailabilityWindow(
                    start_at=_today_at(17, 5),
                    end_at=_today_at(18, 5),
                    location_hint="Libe Slope",
                ),
                AvailabilityWindow(
                    start_at=_today_at(20, 0),
                    end_at=_today_at(21, 0),
                    location_hint="Collegetown",
                ),
            ],
        ),
        FriendAvailability(
            friend_id="f2",
            friend_name="Jonah",
            windows=[
                AvailabilityWindow(
                    start_at=_today_at(17, 10),
                    end_at=_today_at(18, 10),
                    location_hint="Libe Slope",
                ),
                AvailabilityWindow(
                    start_at=_today_at(19, 45),
                    end_at=_today_at(20, 30),
                    location_hint="RPCC",
                ),
            ],
        ),
        FriendAvailability(
            friend_id="f3",
            friend_name="Sana",
            windows=[
                AvailabilityWindow(
                    start_at=_today_at(17, 15),
                    end_at=_today_at(18, 0),
                    location_hint="Libe Slope",
                ),
                AvailabilityWindow(
                    start_at=_today_at(21, 0),
                    end_at=_today_at(22, 0),
                    location_hint="Duffield",
                ),
            ],
        ),
        FriendAvailability(
            friend_id="f4",
            friend_name="Eli",
            windows=[
                AvailabilityWindow(
                    start_at=_today_at(17, 0),
                    end_at=_today_at(17, 55),
                    location_hint="Libe Slope",
                )
            ],
        ),
        FriendAvailability(
            friend_id="f5",
            friend_name="Priya",
            windows=[
                AvailabilityWindow(
                    start_at=_today_at(17, 20),
                    end_at=_today_at(18, 5),
                    location_hint="Libe Slope",
                )
            ],
        ),
    ]


def default_schedule() -> list[ScheduleBlock]:
    return [
        ScheduleBlock(
            id="b1",
            label="Algo lecture",
            block_type="class",
            start_at=_today_at(9, 5),
            end_at=_today_at(10, 20),
            movable=False,
            intensity=1.0,
        ),
        ScheduleBlock(
            id="b2",
            label="Problem Set 4 focus sprint",
            block_type="work",
            start_at=_today_at(15, 50),
            end_at=_today_at(17, 5),
            movable=True,
            intensity=1.0,
        ),
        ScheduleBlock(
            id="b3",
            label="Duffield reset",
            block_type="meal",
            start_at=_today_at(14, 55),
            end_at=_today_at(15, 20),
            movable=True,
            intensity=0.8,
        ),
        ScheduleBlock(
            id="b4",
            label="Reading block",
            block_type="work",
            start_at=_today_at(18, 15),
            end_at=_today_at(19, 0),
            movable=True,
            intensity=0.9,
        ),
        ScheduleBlock(
            id="b5",
            label="Club sync",
            block_type="class",
            start_at=_today_at(19, 0),
            end_at=_today_at(19, 45),
            movable=False,
            intensity=1.0,
        ),
    ]


def default_idle_event() -> IdleEvent:
    return IdleEvent(
        source="mocked_browser_feed",
        app_name="YouTube",
        duration_minutes=20,
        detected_at=_today_at(16, 40),
    )


def default_weather_context() -> WeatherContext:
    return WeatherContext(
        summary="Clear and cold enough to feel like Ithaca earned it.",
        condition="clear",
        temperature_f=58,
    )
