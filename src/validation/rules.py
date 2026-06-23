from __future__ import annotations

import re
from datetime import datetime
from typing import Any


ID_PATTERNS = {
    "school_id": re.compile(r"^SCH_\d{3}$"),
    "student_id": re.compile(r"^STU_\d{5}$"),
    "session_id": re.compile(r"^SES_\d{5}$"),
    "attendance_id": re.compile(r"^ATT_\d{6}$"),
    "assessment_id": re.compile(r"^ASM_\d{6}$"),
    "visit_id": re.compile(r"^VIS_\d{5}$"),
    "facilitator_id": re.compile(r"^FAC_\d{3}$"),
    "collector_id": re.compile(r"^COL_\d{3}$"),
    "device_id": re.compile(r"^DEV_\d{3}$"),
    "module_id": re.compile(r"^MOD_\d{3}$"),
    "survey_id": re.compile(r"^SRV_\d{6}$"),
    "intervention_id": re.compile(r"^INT_\d{5}$"),
    "source_upload_id": re.compile(r"^UPL_\d{5}$"),
}


def parse_date(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def valid_id(field: str, value: Any) -> bool:
    pattern = ID_PATTERNS[field]
    return isinstance(value, str) and bool(pattern.match(value))


def normalize_gender(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if normalized in {"female", "f"}:
        return "Female"
    if normalized in {"male", "m"}:
        return "Male"
    return None


def valid_score(value: Any) -> bool:
    return isinstance(value, (int, float)) and 0 <= value <= 100
