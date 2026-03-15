from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from backend.app.config import settings
from backend.app.schemas import Assignment, ShufflePlan, ScheduleBlock, SocialPocket
from backend.app.services.fateweaver import build_fateweaver_tactics


class FateweaverTacticsSmokeTest(TestCase):
    def setUp(self) -> None:
        self.assignments = [
            Assignment(
                id="a1",
                course_code="CS 3110",
                title="Problem Set 4",
                task_type="pset",
                due_at=datetime(2026, 3, 15, 23, 0),
                base_effort_hours=4.0,
                estimated_weight=4,
                reading_pages=0,
                status="pending",
            ),
            Assignment(
                id="a2",
                course_code="CS 3110",
                title="Reading block",
                task_type="reading",
                due_at=datetime(2026, 3, 16, 10, 0),
                base_effort_hours=1.5,
                estimated_weight=2,
                reading_pages=30,
                status="pending",
            ),
        ]
        self.plan = ShufflePlan(
            before_blocks=[
                ScheduleBlock(
                    id="before-1",
                    label="Problem Set 4 focus sprint",
                    block_type="work",
                    start_at=datetime(2026, 3, 15, 15, 0),
                    end_at=datetime(2026, 3, 15, 16, 0),
                    movable=True,
                    intensity=1.0,
                )
            ],
            after_blocks=[
                ScheduleBlock(
                    id="after-1",
                    label="Late work block",
                    block_type="work",
                    start_at=datetime(2026, 3, 15, 19, 30),
                    end_at=datetime(2026, 3, 15, 20, 15),
                    movable=True,
                    intensity=1.1,
                )
            ],
            target_pocket_id="p1",
            tradeoff_statement="Focus now and you unlock sunset on the Slope.",
            focus_boost_multiplier=1.2,
            unlocked_minutes=45,
        )
        self.target_pocket = SocialPocket(
            id="p1",
            start_at=datetime(2026, 3, 15, 17, 0),
            end_at=datetime(2026, 3, 15, 17, 45),
            title="Sunset on the Slope",
            location_hint="Libe Slope",
            friend_names=["Maya", "Jonah", "Sana"],
            score=92.0,
            claimability="High",
            why_now="Three friends are free at once.",
            activity_suggestion="Sunset on the Slope",
            day_phase="late afternoon",
            weather_label="58F and clear",
            emotional_hook="A reclaimable Cornell hour.",
        )

    def test_rule_based_fallback_returns_three_tactics(self) -> None:
        with patch.object(settings, "OPENAI_API_KEY", None):
            tactics, source = build_fateweaver_tactics(self.assignments, self.plan, self.target_pocket)

        self.assertEqual(source, "rule-based")
        self.assertEqual(len(tactics), 3)
        self.assertTrue(all(tactic for tactic in tactics))

    def test_openai_response_is_used_when_available(self) -> None:
        parsed = SimpleNamespace(
            tactics=[
                "Compress the pset into a first-pass sprint before leaving.",
                "Shift the reading block later so the slope window stays clean.",
                "Protect the last ten minutes before departure from context switching.",
            ]
        )
        mock_client = SimpleNamespace(
            beta=SimpleNamespace(
                chat=SimpleNamespace(
                    completions=SimpleNamespace(
                        parse=lambda **_: SimpleNamespace(
                            choices=[SimpleNamespace(message=SimpleNamespace(parsed=parsed))]
                        )
                    )
                )
            )
        )

        with patch.object(settings, "OPENAI_API_KEY", "test-key"):
            with patch("backend.app.services.fateweaver.OpenAI", return_value=mock_client):
                tactics, source = build_fateweaver_tactics(self.assignments, self.plan, self.target_pocket)

        self.assertEqual(source, "openai")
        self.assertEqual(len(tactics), 3)
        self.assertEqual(tactics[0], parsed.tactics[0])

    def test_openai_failure_falls_back_cleanly(self) -> None:
        with patch.object(settings, "OPENAI_API_KEY", "test-key"):
            with patch("backend.app.services.fateweaver.OpenAI", side_effect=RuntimeError("boom")):
                tactics, source = build_fateweaver_tactics([], self.plan, self.target_pocket)

        self.assertEqual(source, "rule-based")
        self.assertEqual(len(tactics), 3)
