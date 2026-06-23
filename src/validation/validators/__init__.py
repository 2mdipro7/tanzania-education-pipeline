from dataclasses import dataclass, field
from typing import Any

from src.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ValidatorContext:
    school_ids: set[str] = field(default_factory=set)
    facilitator_ids: set[str] = field(default_factory=set)
    collector_ids: set[str] = field(default_factory=set)
    device_ids: set[str] = field(default_factory=set)
    module_ids: set[str] = field(default_factory=set)
    student_ids: set[str] = field(default_factory=set)
    session_ids: set[str] = field(default_factory=set)
    session_school_lookup: dict[str, str] = field(default_factory=dict)
    seen_attendance_keys: set[tuple[str, str]] = field(default_factory=set)
