from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from .mock_data import (
    default_assignments,
    default_course,
    default_friend_availability,
    default_idle_event,
    default_schedule,
    default_user_profile,
    default_weather_context,
)
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


DB_PATH = Path(__file__).resolve().parent.parent / "kairos.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
DEMO_USER_ID = "demo-user"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
      connection.executescript(SCHEMA_PATH.read_text())
      
      # Basic migration: try adding new columns safely
      try:
          connection.execute("ALTER TABLE users ADD COLUMN google_access_token TEXT")
          connection.execute("ALTER TABLE users ADD COLUMN google_refresh_token TEXT")
          connection.execute("ALTER TABLE users ADD COLUMN token_expiry DATETIME")
      except sqlite3.OperationalError:
          pass # Columns already exist
          
      seeded = connection.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
      if seeded:
          return

      user = default_user_profile()
      course = default_course()
      assignments = default_assignments()
      friends = default_friend_availability()
      schedule = default_schedule()
      idle_event = default_idle_event()
      weather = default_weather_context()

      connection.execute(
          """
          INSERT INTO users (
              id, name, email, major, reading_speed_pph,
              major_difficulty_multiplier, historical_productivity_multiplier,
              social_readiness_goal_hours
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
          """,
          (
              DEMO_USER_ID,
              user["name"],
              user["email"],
              user["major"],
              user["reading_speed_pph"],
              user["major_difficulty_multiplier"],
              user["historical_productivity_multiplier"],
              user["social_readiness_goal_hours"],
          ),
      )
      connection.execute(
          "INSERT INTO courses (id, user_id, code, title, syllabus_source) VALUES (?, ?, ?, ?, ?)",
          ("course-1", DEMO_USER_ID, course.code, course.title, "mocked-syllabus.pdf"),
      )
      connection.executemany(
          """
          INSERT INTO assignments (
              id, user_id, course_code, title, task_type, due_at,
              base_effort_hours, estimated_weight, reading_pages, status
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          """,
          [
              (
                  assignment.id,
                  DEMO_USER_ID,
                  assignment.course_code,
                  assignment.title,
                  assignment.task_type,
                  assignment.due_at.isoformat(),
                  assignment.base_effort_hours,
                  assignment.estimated_weight,
                  assignment.reading_pages,
                  assignment.status,
              )
              for assignment in assignments
          ],
      )
      for friend in friends:
          connection.execute(
              "INSERT INTO friends (id, user_id, friend_name, home_zone) VALUES (?, ?, ?, ?)",
              (friend.friend_id, DEMO_USER_ID, friend.friend_name, "Collegetown"),
          )
          connection.executemany(
              "INSERT INTO availability_windows (friend_id, start_at, end_at, location_hint) VALUES (?, ?, ?, ?)",
              [
                  (
                      friend.friend_id,
                      window.start_at.isoformat(),
                      window.end_at.isoformat(),
                      window.location_hint,
                  )
                  for window in friend.windows
              ],
          )

      connection.executemany(
          """
          INSERT INTO schedule_blocks (
              id, user_id, label, block_type, start_at, end_at, movable, intensity
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
          """,
          [
              (
                  block.id,
                  DEMO_USER_ID,
                  block.label,
                  block.block_type,
                  block.start_at.isoformat(),
                  block.end_at.isoformat(),
                  int(block.movable),
                  block.intensity,
              )
              for block in schedule
          ],
      )
      connection.execute(
          "INSERT INTO idle_events (user_id, source, app_name, duration_minutes, detected_at) VALUES (?, ?, ?, ?, ?)",
          (
              DEMO_USER_ID,
              idle_event.source,
              idle_event.app_name,
              idle_event.duration_minutes,
              idle_event.detected_at.isoformat(),
          ),
      )
      connection.execute(
          "INSERT INTO weather_context (id, summary, condition, temperature_f) VALUES (1, ?, ?, ?)",
          (weather.summary, weather.condition, weather.temperature_f),
      )


def load_demo_snapshot() -> tuple[
    UserAssumptions,
    Course,
    list[Assignment],
    list[FriendAvailability],
    list[ScheduleBlock],
    IdleEvent,
    WeatherContext,
]:
    with get_connection() as connection:
        user_row = connection.execute("SELECT * FROM users WHERE id = ?", (DEMO_USER_ID,)).fetchone()
        assumptions = UserAssumptions(
            reading_speed_pph=user_row["reading_speed_pph"],
            major_difficulty_multiplier=user_row["major_difficulty_multiplier"],
            historical_productivity_multiplier=user_row["historical_productivity_multiplier"],
            social_readiness_goal_hours=user_row["social_readiness_goal_hours"],
        )
        course_row = connection.execute(
            "SELECT code, title FROM courses WHERE user_id = ? ORDER BY rowid DESC LIMIT 1", (DEMO_USER_ID,)
        ).fetchone()
        course = Course(code=course_row["code"], title=course_row["title"])
        assignment_rows = connection.execute(
            "SELECT * FROM assignments WHERE user_id = ? ORDER BY due_at ASC", (DEMO_USER_ID,)
        ).fetchall()
        assignments = [
            Assignment(
                id=row["id"],
                course_code=row["course_code"],
                title=row["title"],
                task_type=row["task_type"],
                due_at=datetime.fromisoformat(row["due_at"]),
                base_effort_hours=row["base_effort_hours"],
                estimated_weight=row["estimated_weight"],
                reading_pages=row["reading_pages"],
                status=row["status"],
            )
            for row in assignment_rows
        ]
        friend_rows = connection.execute("SELECT * FROM friends WHERE user_id = ?", (DEMO_USER_ID,)).fetchall()
        friends: list[FriendAvailability] = []
        for row in friend_rows:
            window_rows = connection.execute(
                "SELECT * FROM availability_windows WHERE friend_id = ? ORDER BY start_at ASC", (row["id"],)
            ).fetchall()
            friends.append(
                FriendAvailability(
                    friend_id=row["id"],
                    friend_name=row["friend_name"],
                    windows=[
                        {
                            "start_at": datetime.fromisoformat(window["start_at"]),
                            "end_at": datetime.fromisoformat(window["end_at"]),
                            "location_hint": window["location_hint"],
                        }
                        for window in window_rows
                    ],
                )
            )
        schedule_rows = connection.execute(
            "SELECT * FROM schedule_blocks WHERE user_id = ? ORDER BY start_at ASC", (DEMO_USER_ID,)
        ).fetchall()
        schedule = [
            ScheduleBlock(
                id=row["id"],
                label=row["label"],
                block_type=row["block_type"],
                start_at=datetime.fromisoformat(row["start_at"]),
                end_at=datetime.fromisoformat(row["end_at"]),
                movable=bool(row["movable"]),
                intensity=row["intensity"],
            )
            for row in schedule_rows
        ]
        idle_row = connection.execute(
            "SELECT * FROM idle_events WHERE user_id = ? ORDER BY detected_at DESC LIMIT 1", (DEMO_USER_ID,)
        ).fetchone()
        idle_event = IdleEvent(
            source=idle_row["source"],
            app_name=idle_row["app_name"],
            duration_minutes=idle_row["duration_minutes"],
            detected_at=datetime.fromisoformat(idle_row["detected_at"]),
        )
        weather_row = connection.execute("SELECT * FROM weather_context WHERE id = 1").fetchone()
        weather = WeatherContext(
            summary=weather_row["summary"],
            condition=weather_row["condition"],
            temperature_f=weather_row["temperature_f"],
        )
        return assumptions, course, assignments, friends, schedule, idle_event, weather


def upsert_user(
    user_id: str,
    name: str,
    email: str,
    access_token: str,
    refresh_token: str | None,
    token_expiry: str | None,
) -> None:
    with get_connection() as connection:
        user = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user:
            connection.execute(
                """
                UPDATE users
                SET name = ?, email = ?, google_access_token = ?, google_refresh_token = COALESCE(?, google_refresh_token), token_expiry = ?
                WHERE id = ?
                """,
                (name, email, access_token, refresh_token, token_expiry, user_id),
            )
        else:
            # Seed the default assumptions for a new user
            connection.execute(
                """
                INSERT INTO users (
                    id, name, email, major, reading_speed_pph,
                    major_difficulty_multiplier, historical_productivity_multiplier,
                    social_readiness_goal_hours, google_access_token, google_refresh_token, token_expiry
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id, name, email, "Undeclared", 28, 1.1, 0.95, 6.0,
                    access_token, refresh_token, token_expiry
                ),
            )
            # Seed basic mock data so their dashboard isn't completely empty
            connection.execute(
                "INSERT INTO weather_context (id, summary, condition, temperature_f) VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING",
                (1, "Sunset approaching", "clear", 68)
            )

def get_user_tokens(user_id: str) -> dict | None:
    with get_connection() as connection:
        row = connection.execute("SELECT google_access_token, google_refresh_token FROM users WHERE id = ?", (user_id,)).fetchone()
        if row and row["google_access_token"]:
            return dict(row)
        return None

def save_schedule_blocks(user_id: str, blocks: list[ScheduleBlock]) -> None:
    with get_connection() as connection:
        # Clear existing schedule blocks for this user
        connection.execute("DELETE FROM schedule_blocks WHERE user_id = ?", (user_id,))
        # Insert new ones
        if not blocks: return
        connection.executemany(
            """
            INSERT INTO schedule_blocks (id, user_id, label, block_type, start_at, end_at, movable, intensity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    block.id,
                    user_id,
                    block.label,
                    block.block_type,
                    block.start_at.isoformat(),
                    block.end_at.isoformat(),
                    int(block.movable),
                    block.intensity,
                )
                for block in blocks
            ],
        )

def get_user_schedule(user_id: str) -> list[ScheduleBlock]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM schedule_blocks WHERE user_id = ?", (user_id,)).fetchall()
        return [
            ScheduleBlock(
                id=r["id"],
                label=r["label"],
                block_type=r["block_type"],
                start_at=datetime.fromisoformat(r["start_at"]),
                end_at=datetime.fromisoformat(r["end_at"]),
                movable=bool(r["movable"]),
                intensity=r["intensity"],
            )
            for r in rows
        ]

def get_user_assignments(user_id: str) -> tuple[Course, list[Assignment]]:
    with get_connection() as connection:
        course_row = connection.execute("SELECT * FROM courses WHERE user_id = ?", (user_id,)).fetchone()
        if not course_row:
             # Return empty mock if none exists
             return Course(code="NONE 101", title="No Courses Yet"), []
             
        course = Course(code=course_row["code"], title=course_row["title"])
        
        assignment_rows = connection.execute("SELECT * FROM assignments WHERE user_id = ?", (user_id,)).fetchall()
        assignments = [
            Assignment(
                id=r["id"],
                course_code=r["course_code"],
                title=r["title"],
                task_type=r["task_type"],
                due_at=datetime.fromisoformat(r["due_at"]),
                base_effort_hours=r["base_effort_hours"],
                estimated_weight=r["estimated_weight"],
                reading_pages=r["reading_pages"],
                status=r["status"],
            )
            for r in assignment_rows
        ]
        return course, assignments

def get_user_friends(user_id: str) -> list[FriendAvailability]:
    with get_connection() as connection:
        friend_rows = connection.execute("SELECT * FROM friends WHERE user_id = ?", (user_id,)).fetchall()
        
        friends = []
        for f_row in friend_rows:
            window_rows = connection.execute("SELECT * FROM availability_windows WHERE friend_id = ?", (f_row["id"],)).fetchall()
            windows = [
                AvailabilityWindow(
                    start_at=datetime.fromisoformat(w["start_at"]),
                    end_at=datetime.fromisoformat(w["end_at"]),
                    location_hint=w["location_hint"],
                )
                for w in window_rows
            ]
            friends.append(
                FriendAvailability(
                    friend_id=f_row["id"],
                    friend_name=f_row["friend_name"],
                    windows=windows
                )
            )
        return friends

def get_user_assumptions(user_id: str) -> UserAssumptions:
    with get_connection() as connection:
        user_row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return UserAssumptions(
            reading_speed_pph=user_row["reading_speed_pph"],
            major_difficulty_multiplier=user_row["major_difficulty_multiplier"],
            historical_productivity_multiplier=user_row["historical_productivity_multiplier"],
            social_readiness_goal_hours=user_row["social_readiness_goal_hours"],
        )


def replace_assignments(user_id: str, course: Course, assignments: list[Assignment]) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM courses WHERE user_id = ?", (user_id,))
        connection.execute("DELETE FROM assignments WHERE user_id = ?", (user_id,))
        connection.execute(
            "INSERT INTO courses (id, user_id, code, title, syllabus_source) VALUES (?, ?, ?, ?, ?)",
            ("course-upload", user_id, course.code, course.title, "uploaded"),
        )
        connection.executemany(
            """
            INSERT INTO assignments (
                id, user_id, course_code, title, task_type, due_at,
                base_effort_hours, estimated_weight, reading_pages, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    assignment.id,
                    user_id,
                    assignment.course_code,
                    assignment.title,
                    assignment.task_type,
                    assignment.due_at.isoformat(),
                    assignment.base_effort_hours,
                    assignment.estimated_weight,
                    assignment.reading_pages,
                    assignment.status,
                )
                for assignment in assignments
            ],
        )

def update_user_assumptions(user_id: str, assumptions: UserAssumptions) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE users
            SET reading_speed_pph = ?,
                major_difficulty_multiplier = ?,
                historical_productivity_multiplier = ?,
                social_readiness_goal_hours = ?
            WHERE id = ?
            """,
            (
                assumptions.reading_speed_pph,
                assumptions.major_difficulty_multiplier,
                assumptions.historical_productivity_multiplier,
                assumptions.social_readiness_goal_hours,
                user_id,
            ),
        )
