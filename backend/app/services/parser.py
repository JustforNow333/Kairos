from __future__ import annotations

from .scheduler import build_work_debt_ledger
from ..mock_data import default_assignments, default_assumptions, default_course
from ..schemas import SyllabusParseResponse


def parse_syllabus(filename: str | None = None, file_bytes: bytes | None = None) -> SyllabusParseResponse:
    course = default_course()
    assignments = default_assignments()
    assumptions = default_assumptions()

    if filename and "econ" in filename.lower():
        course = course.model_copy(update={"code": "ECON 1110", "title": "Introductory Microeconomics"})
        assignments = [assignment.model_copy(update={"course_code": "ECON 1110"}) for assignment in assignments]

    ledger = build_work_debt_ledger(assignments, assumptions)
    return SyllabusParseResponse(
        course=course,
        assignments=assignments,
        ledger=ledger,
        parser_mode="mock-gpt4o-adapter",
        notes="Starter implementation uses deterministic mock extraction behind a replaceable parser abstraction.",
    )
