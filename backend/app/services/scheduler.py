from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from ..schemas import (
    Assignment,
    FriendAvailability,
    IdleAlert,
    IdleEvent,
    ScheduleBlock,
    SocialReadiness,
    ShufflePlan,
    SocialPocket,
    UserAssumptions,
    WeatherContext,
    WorkDebtItem,
    WorkDebtLedger,
)


def _hours_until(deadline: datetime, now: datetime) -> float:
    return max((deadline - now).total_seconds() / 3600, 0.0)


def _interest_multiplier(deadline: datetime, now: datetime) -> float:
    hours_left = _hours_until(deadline, now)
    if hours_left <= 12:
        return 1.9
    if hours_left <= 24:
        return 1.6
    if hours_left <= 48:
        return 1.35
    if hours_left <= 72:
        return 1.2
    return 1.05


def _adjusted_effort(assignment: Assignment, assumptions: UserAssumptions) -> float:
    effort = assignment.base_effort_hours * assumptions.major_difficulty_multiplier
    if assignment.task_type == "reading" and assignment.reading_pages:
        reading_hours = assignment.reading_pages / max(assumptions.reading_speed_pph, 1)
        effort = max(effort, reading_hours)
    return round(effort / max(assumptions.historical_productivity_multiplier, 0.6), 2)


def build_work_debt_ledger(
    assignments: list[Assignment], assumptions: UserAssumptions, now: datetime | None = None
) -> WorkDebtLedger:
    now = now or datetime.now()
    items: list[WorkDebtItem] = []
    total_hours = 0.0
    debt_score = 0.0
    interest_drag = 0.0

    for assignment in assignments:
        adjusted = _adjusted_effort(assignment, assumptions)
        interest = _interest_multiplier(assignment.due_at, now)
        contribution = round(adjusted * interest * (1 + assignment.estimated_weight / 10), 2)
        items.append(
            WorkDebtItem(
                assignment_id=assignment.id,
                title=assignment.title,
                adjusted_effort_hours=adjusted,
                interest_multiplier=interest,
                debt_contribution=contribution,
                due_at=assignment.due_at,
            )
        )
        total_hours += adjusted
        debt_score += contribution
        interest_drag += adjusted * max(interest - 1, 0)

    focus_hours_today = round(min(total_hours, 4.5), 1)
    summary = (
        "Your next 48 hours are still recoverable, but procrastination is already eating into tomorrow night."
    )

    return WorkDebtLedger(
        work_debt_score=round(debt_score, 1),
        total_hours=round(total_hours, 1),
        interest_drag_hours=round(interest_drag, 1),
        focus_hours_today=focus_hours_today,
        summary=summary,
        items=sorted(items, key=lambda item: item.due_at),
    )


def _day_phase(moment: datetime) -> str:
    hour = moment.hour
    if hour < 11:
        return "morning"
    if hour < 15:
        return "midday"
    if hour < 18:
        return "late afternoon"
    return "evening"


def _activity_suggestion(
    location_hint: str, day_phase: str, weather: WeatherContext, duration_minutes: int, friend_count: int
) -> tuple[str, str]:
    slope_like = "slope" in location_hint.lower()
    if slope_like and weather.condition == "clear" and day_phase in {"late afternoon", "evening"}:
        return (
            "Sunset at the Slope",
            f"{friend_count} friends, golden light, and a window that disappears the moment dinner plans scatter.",
        )
    if day_phase == "evening":
        return ("Quick Collegetown dinner run", "Just enough time to get out, reset, and still keep the night intact.")
    if duration_minutes <= 45:
        return ("Study break walk", "Short enough to feel free, long enough to stop the day from collapsing into scrolling.")
    return ("Ho Plaza reset lap", "It is a realistic window, not a fantasy calendar event.")


def _score_pocket(
    friend_count: int,
    duration_minutes: int,
    start_at: datetime,
    location_hint: str,
    weather: WeatherContext,
) -> tuple[float, str, str]:
    hours_left = max(_hours_until(start_at, datetime.now().replace(second=0, microsecond=0)), 0.1)
    day_phase = _day_phase(start_at)
    urgency = max(0, 16 - (hours_left * 3.5))
    duration_bonus = 12 if duration_minutes in {45, 60} else 8
    context_bonus = 10 if weather.condition == "clear" and "slope" in location_hint.lower() else 5
    score = round((friend_count * 18) + urgency + duration_bonus + context_bonus, 1)
    suggestion, hook = _activity_suggestion(location_hint, day_phase, weather, duration_minutes, friend_count)
    return score, suggestion, hook


def find_social_pockets(friends: list[FriendAvailability], weather: WeatherContext) -> list[SocialPocket]:
    now = datetime.now().replace(second=0, microsecond=0)
    rounded_now = now - timedelta(minutes=now.minute % 15)
    latest_end = max(window.end_at for friend in friends for window in friend.windows)
    candidates: dict[tuple[datetime, datetime], SocialPocket] = {}

    cursor = rounded_now
    while cursor <= latest_end - timedelta(minutes=30):
        for duration_minutes in (45, 60, 30, 75, 90):
            end_at = cursor + timedelta(minutes=duration_minutes)
            if end_at > latest_end:
                continue

            available_names: list[str] = []
            matching_locations: list[str] = []
            for friend in friends:
                for window in friend.windows:
                    if window.start_at <= cursor and window.end_at >= end_at:
                        available_names.append(friend.friend_name)
                        matching_locations.append(window.location_hint)
                        break

            if len(available_names) < 2:
                continue

            location_hint = Counter(matching_locations).most_common(1)[0][0]
            score, suggestion, hook = _score_pocket(
                len(available_names), duration_minutes, cursor, location_hint, weather
            )
            day_phase = _day_phase(cursor)
            pocket = SocialPocket(
                id=f"p{cursor.hour}{cursor.minute}-{duration_minutes}",
                start_at=cursor,
                end_at=end_at,
                title=suggestion,
                location_hint=location_hint,
                friend_names=available_names,
                score=score,
                claimability="High" if len(available_names) >= 4 else "Medium",
                why_now=f"{len(available_names)} friends are simultaneously free for a realistic {duration_minutes}-minute window.",
                activity_suggestion=suggestion,
                day_phase=day_phase,
                weather_label=f"{weather.temperature_f}F and {weather.condition}",
                emotional_hook=hook,
            )
            key = (cursor, end_at)
            existing = candidates.get(key)
            if existing is None or pocket.score > existing.score:
                candidates[key] = pocket
        cursor += timedelta(minutes=15)

    return sorted(candidates.values(), key=lambda pocket: pocket.score, reverse=True)[:4]


def build_social_readiness(
    schedule: list[ScheduleBlock],
    pockets: list[SocialPocket],
    assumptions: UserAssumptions,
) -> SocialReadiness:
    scheduled_social_hours = sum(
        (block.end_at - block.start_at).total_seconds() / 3600 for block in schedule if block.block_type == "social"
    )
    opportunity_hours = 0.0
    if pockets:
        opportunity_hours = min(
            sum((pocket.end_at - pocket.start_at).total_seconds() / 3600 for pocket in pockets[:2]),
            2.5,
        )
    projected_hours = round(scheduled_social_hours + opportunity_hours + 2.2, 1)
    gap_hours = round(max(assumptions.social_readiness_goal_hours - projected_hours, 0), 1)
    score = round(min((projected_hours / assumptions.social_readiness_goal_hours) * 100, 100), 1)
    status = "behind" if gap_hours > 1 else "on track"
    summary = (
        "You are academically covered, but your week still needs one deliberate social window."
        if status == "behind"
        else "Your week has enough social oxygen if you claim the right window."
    )
    return SocialReadiness(
        score=score,
        weekly_target_hours=assumptions.social_readiness_goal_hours,
        projected_hours=projected_hours,
        gap_hours=gap_hours,
        status=status,
        summary=summary,
    )


def _find_gap(
    occupied: list[tuple[datetime, datetime]],
    earliest_start: datetime,
    latest_end: datetime,
    required_minutes: int,
) -> tuple[datetime, int] | None:
    pointer = earliest_start
    for start_at, end_at in sorted(occupied):
        if start_at <= pointer:
            pointer = max(pointer, end_at)
            continue
        available = int((start_at - pointer).total_seconds() / 60)
        if available >= required_minutes:
            return pointer, required_minutes
        if available >= int(required_minutes / 1.25):
            return pointer, available
        pointer = max(pointer, end_at)
    tail = int((latest_end - pointer).total_seconds() / 60)
    if tail >= required_minutes:
        return pointer, required_minutes
    if tail >= int(required_minutes / 1.25):
        return pointer, tail
    return None


def build_shuffle_plan(schedule: list[ScheduleBlock], pockets: list[SocialPocket]) -> ShufflePlan:
    if not pockets:
        raise ValueError("At least one social pocket is required to build a shuffle plan.")

    target = pockets[0]
    conflict_blocks = [
        block
        for block in schedule
        if block.movable and block.start_at < target.end_at and block.end_at > target.start_at
    ]
    stationary_blocks = [block for block in schedule if block not in conflict_blocks]
    occupied = [
        (block.start_at, block.end_at)
        for block in stationary_blocks
        if block.end_at <= target.start_at
    ]
    day_start = min(block.start_at for block in schedule).replace(hour=8, minute=30)
    moved_blocks: list[ScheduleBlock] = []
    focus_boost = 1.0

    for block in sorted(conflict_blocks, key=lambda item: item.start_at):
        original_minutes = int((block.end_at - block.start_at).total_seconds() / 60)
        gap = _find_gap(occupied, day_start, target.start_at - timedelta(minutes=10), original_minutes)
        if gap is None:
            shifted_start = block.start_at - timedelta(minutes=75)
            shifted_end = shifted_start + timedelta(minutes=original_minutes)
            moved_blocks.append(
                block.model_copy(
                    update={"start_at": shifted_start, "end_at": shifted_end, "intensity": 1.2}
                )
            )
            occupied.append((shifted_start, shifted_end))
            focus_boost = max(focus_boost, 1.2)
            continue

        new_start, available_minutes = gap
        new_end = new_start + timedelta(minutes=available_minutes)
        boost = round(original_minutes / available_minutes, 2)
        focus_boost = max(focus_boost, boost)
        moved_blocks.append(
            block.model_copy(
                update={
                    "start_at": new_start,
                    "end_at": new_end,
                    "intensity": round(block.intensity * boost, 2),
                }
            )
        )
        occupied.append((new_start, new_end))

    after_blocks = [block for block in stationary_blocks if block.id not in {moved.id for moved in moved_blocks}]
    after_blocks.extend(moved_blocks)
    after_blocks.append(
        ScheduleBlock(
            id="social-pocket",
            label=target.title,
            block_type="social",
            start_at=target.start_at,
            end_at=target.end_at,
            movable=False,
            intensity=1.0,
        )
    )

    friend_count = len(target.friend_names)
    boost_string = f"{focus_boost:.2f}".rstrip("0").rstrip(".")
    return ShufflePlan(
        before_blocks=sorted(schedule, key=lambda block: block.start_at),
        after_blocks=sorted(after_blocks, key=lambda block: block.start_at),
        target_pocket_id=target.id,
        tradeoff_statement=(
            f"If you focus for the next hour at {boost_string}x pace, you unlock "
            f"{target.title} with {friend_count} friends."
        ),
        focus_boost_multiplier=focus_boost,
        unlocked_minutes=int((target.end_at - target.start_at).total_seconds() / 60),
    )


def build_idle_alert(
    idle_event: IdleEvent,
    pockets: list[SocialPocket],
    assumptions: UserAssumptions,
    social_readiness: SocialReadiness,
) -> IdleAlert:
    target = pockets[0]
    return IdleAlert(
        headline=f"Trade-off Alert: {idle_event.duration_minutes} mins of {idle_event.app_name} vs. {target.title}.",
        action=(
            "Take the reshuffled focus sprint now, leave in 12 minutes, and keep your week from becoming all work and no memory."
        ),
        social_readiness_gap_hours=social_readiness.gap_hours,
        friend_names=target.friend_names,
        target_pocket_id=target.id,
    )
