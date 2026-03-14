from __future__ import annotations

import io
import uuid
from datetime import datetime
from typing import Literal

import pdfplumber
from openai import OpenAI
from pydantic import BaseModel

from .scheduler import build_work_debt_ledger
from ..mock_data import default_assignments, default_assumptions, default_course
from ..schemas import Assignment, Course, SyllabusParseResponse
from ..config import settings


class ExtractedAssignment(BaseModel):
    title: str
    task_type: Literal["pset", "reading", "essay", "lab", "exam_prep"]
    due_at: datetime
    base_effort_hours: float
    estimated_weight: int
    reading_pages: int


class ExtractedSyllabus(BaseModel):
    course_code: str
    course_title: str
    assignments: list[ExtractedAssignment]


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    return file_bytes.decode("utf-8", errors="ignore")


def parse_syllabus(filename: str | None = None, file_bytes: bytes | None = None) -> SyllabusParseResponse:
    if settings.USE_MOCK_DATA or not settings.OPENAI_API_KEY:
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
    
    if not file_bytes or not filename:
        raise ValueError("file_bytes and filename are required for live parsing")
        
    text = extract_text_from_bytes(file_bytes, filename)
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "You are an expert AI syllabus extractor. Your job is to extract the course code, course title, and a comprehensive list of all assignments, problem sets, essays, and readings from the provided syllabus text. Estimate effort hours and weight out of 5 for each based on realistic college expectations. Assume current year if missing."
            },
            {
                "role": "user",
                "content": f"Extract syllabus details from the following text:\n\n{text[:15000]}"
            }
        ],
        response_format=ExtractedSyllabus,
    )
    
    extracted = response.choices[0].message.parsed
    course = Course(code=extracted.course_code, title=extracted.course_title)
    
    assignments = []
    for ext_a in extracted.assignments:
        assignments.append(Assignment(
            id=str(uuid.uuid4())[:8],
            course_code=course.code,
            title=ext_a.title,
            task_type=ext_a.task_type,
            due_at=ext_a.due_at,
            base_effort_hours=ext_a.base_effort_hours,
            estimated_weight=ext_a.estimated_weight,
            reading_pages=ext_a.reading_pages,
            status="pending"
        ))
    
    assumptions = default_assumptions()
    ledger = build_work_debt_ledger(assignments, assumptions)
    return SyllabusParseResponse(
        course=course,
        assignments=assignments,
        ledger=ledger,
        parser_mode="gpt-4o-live",
        notes="Parsed successfully using OpenAI gpt-4o structured extraction.",
    )
