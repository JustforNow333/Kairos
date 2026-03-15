from __future__ import annotations

from pydantic import BaseModel
from openai import OpenAI

from ..config import settings
from ..schemas import Assignment, ShufflePlan, SocialPocket


class FateweaverTacticsResponse(BaseModel):
    tactics: list[str]


def build_rule_based_tactics(
    assignments: list[Assignment],
    plan: ShufflePlan,
    target_pocket: SocialPocket | None,
) -> list[str]:
    target_label = target_pocket.title if target_pocket else "this window"
    tactics: list[str] = []
    sprint_minutes = min(max(round(plan.unlocked_minutes / 2), 20), 30)

    reading_assignment = next(
        (
            assignment
            for assignment in assignments
            if assignment.status != "done" and assignment.task_type == "reading"
        ),
        None,
    )
    if reading_assignment:
        tactics.append(
            f"Compress {reading_assignment.title} into a discussion-only pass so {target_label} stays claimable."
        )

    pset_like_assignment = next(
        (
            assignment
            for assignment in assignments
            if assignment.status != "done" and assignment.task_type in {"pset", "lab"}
        ),
        None,
    )
    if pset_like_assignment:
        tactics.append(
            f"Front-load the fastest wins in {pset_like_assignment.title} before you leave so the day still feels under control."
        )

    later_work_block = next(
        (
            block
            for block in plan.after_blocks
            if block.block_type == "work" and block.start_at.hour >= 19
        ),
        None,
    )
    if later_work_block:
        tactics.append(
            f"Push {later_work_block.label} into the quieter late block and protect the cleanest hour for {target_label}."
        )

    fallback_pool = [
        f"Run a {sprint_minutes}-minute distraction-free sprint now. Fateweaver Protocol only needs one clean burst to unlock {target_label}.",
        f"Treat the next block like a tactical unlock, not a full-day recovery plan. You only need enough momentum to make {target_label} cleanly reachable.",
        f"Protect the transition into {target_label} by cutting setup friction now so leaving the work block is a clean decision, not a debate.",
    ]
    for fallback in fallback_pool:
        if len(tactics) >= 3:
            break
        tactics.append(fallback)

    return tactics[:3]


def _build_prompt(assignments: list[Assignment], plan: ShufflePlan, target_pocket: SocialPocket | None) -> str:
    assignment_lines = [
        f"- {assignment.title} ({assignment.task_type}, due {assignment.due_at.isoformat()}, {assignment.base_effort_hours}h, status={assignment.status})"
        for assignment in assignments[:6]
    ]
    moved_block_lines = [
        f"- {block.label}: {block.start_at.isoformat()} to {block.end_at.isoformat()}, intensity={block.intensity}"
        for block in plan.after_blocks
        if block.block_type == "work"
    ]
    pocket_line = (
        f"{target_pocket.title} at {target_pocket.location_hint} with {', '.join(target_pocket.friend_names)}"
        if target_pocket
        else "the selected social window"
    )

    return (
        "Generate exactly 3 tactical Fateweaver Protocol suggestions.\n"
        "Each suggestion must be specific to unlocking the selected social window.\n"
        "Avoid generic productivity advice. Keep each tactic to one sentence.\n\n"
        f"Target window: {pocket_line}\n"
        f"Tradeoff statement: {plan.tradeoff_statement}\n"
        "Assignments:\n"
        f"{chr(10).join(assignment_lines) or '- No assignments provided'}\n"
        "Rewoven work blocks:\n"
        f"{chr(10).join(moved_block_lines) or '- No moved work blocks provided'}"
    )


def build_fateweaver_tactics(
    assignments: list[Assignment],
    plan: ShufflePlan,
    target_pocket: SocialPocket | None,
) -> tuple[list[str], str]:
    fallback_tactics = build_rule_based_tactics(assignments, plan, target_pocket)
    if not settings.OPENAI_API_KEY:
        return fallback_tactics, "rule-based"

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You write Fateweaver Protocol tactics for a Cornell-first life operating system. "
                        "Your output should feel tactical, grounded in the actual schedule rewrite, and emotionally aware without sounding generic."
                    ),
                },
                {
                    "role": "user",
                    "content": _build_prompt(assignments, plan, target_pocket),
                },
            ],
            response_format=FateweaverTacticsResponse,
        )
        parsed = response.choices[0].message.parsed
        if not parsed:
            return fallback_tactics, "rule-based"

        tactics = [tactic.strip() for tactic in parsed.tactics if tactic.strip()]
        if not tactics:
            return fallback_tactics, "rule-based"
        if len(tactics) < 3:
            tactics.extend(fallback_tactics)

        return tactics[:3], "openai"
    except Exception:
        return fallback_tactics, "rule-based"
