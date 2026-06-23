from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.db import get_database
from src.validation.data_quality_checks import run_post_clean_quality_checks
from src.logging_config import get_logger

from src.validation.validators import ValidatorContext
from src.validation.validators.schools import validate_schools
from src.validation.validators.facilitators import validate_facilitators
from src.validation.validators.common import (
    validate_data_collectors, validate_field_devices, validate_curriculum_modules,
    validate_facilitator_visits, validate_student_surveys, validate_program_targets,
    validate_source_uploads, validate_interventions
)
from src.validation.validators.students import validate_students
from src.validation.validators.sessions import validate_sessions
from src.validation.validators.attendance import validate_attendance
from src.validation.validators.assessments import validate_assessments

logger = get_logger(__name__)


RAW_ID_FIELDS = {
    "raw_schools": "school_id",
    "raw_facilitators": "facilitator_id",
    "raw_data_collectors": "collector_id",
    "raw_field_devices": "device_id",
    "raw_curriculum_modules": "module_id",
    "raw_students": "student_id",
    "raw_sessions": "session_id",
    "raw_attendance": "attendance_id",
    "raw_assessments": "assessment_id",
    "raw_facilitator_visits": "visit_id",
    "raw_student_surveys": "survey_id",
    "raw_program_targets": "target_id",
    "raw_source_uploads": "source_upload_id",
    "raw_interventions": "intervention_id",
}


def replace_collection(db, name: str, documents: list[dict[str, Any]]) -> None:
    db[name].delete_many({})
    if documents:
        db[name].insert_many(documents)


def build_quarantine_records(db, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    quarantine_records = []
    for quality_issue in issues:
        source_collection = quality_issue["collection"]
        id_field = RAW_ID_FIELDS.get(source_collection)
        raw_record = None
        if id_field and quality_issue.get("record_id") is not None:
            raw_record = db[source_collection].find_one(
                {id_field: quality_issue["record_id"]},
                {"_id": 0},
            )
        quarantine_records.append(
            {
                "source_collection": source_collection,
                "record_id": quality_issue.get("record_id"),
                "issue_type": quality_issue.get("issue_type"),
                "severity": quality_issue.get("severity"),
                "field": quality_issue.get("field"),
                "batch_id": quality_issue.get("batch_id"),
                "school_id": quality_issue.get("school_id"),
                "detected_at": quality_issue.get("detected_at"),
                "raw_record": raw_record,
            }
        )
    return quarantine_records


def build_clean_collections() -> dict[str, Any]:
    db = get_database()
    ctx = ValidatorContext()
    quality_issues: list[dict[str, Any]] = []

    # 1. Independent collections
    clean_schools, issues = validate_schools(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "schools", clean_schools)

    clean_facilitators, issues = validate_facilitators(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "facilitators", clean_facilitators)

    clean_collectors, issues = validate_data_collectors(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "data_collectors", clean_collectors)

    clean_modules, issues = validate_curriculum_modules(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "curriculum_modules", clean_modules)

    # 2. First-level dependencies
    clean_devices, issues = validate_field_devices(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "field_devices", clean_devices)

    clean_students, issues = validate_students(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "students", clean_students)

    clean_sessions, issues = validate_sessions(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "sessions", clean_sessions)

    # 3. Second-level dependencies
    clean_attendance, issues = validate_attendance(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "attendance", clean_attendance)

    clean_assessments, issues = validate_assessments(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "assessments", clean_assessments)

    clean_visits, issues = validate_facilitator_visits(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "facilitator_visits", clean_visits)

    clean_surveys, issues = validate_student_surveys(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "student_surveys", clean_surveys)

    clean_targets, issues = validate_program_targets(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "program_targets", clean_targets)

    clean_uploads, issues = validate_source_uploads(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "source_uploads", clean_uploads)

    clean_interventions, issues = validate_interventions(db, ctx)
    quality_issues.extend(issues)
    replace_collection(db, "interventions", clean_interventions)

    # Post-clean quality checks and quarantine
    quality_issues.extend(run_post_clean_quality_checks(db))
    quarantine_records = build_quarantine_records(db, quality_issues)
    replace_collection(db, "quality_issues", quality_issues)
    replace_collection(db, "quarantine_records", quarantine_records)

    logger.info(f"Cleaned collections and logged {len(quality_issues)} quality issues")

    clean_collections = [
        "schools", "facilitators", "data_collectors", "field_devices",
        "curriculum_modules", "students", "sessions", "attendance",
        "assessments", "facilitator_visits", "student_surveys",
        "program_targets", "source_uploads", "interventions",
    ]

    return {
        "clean_counts": {
            collection_name: db[collection_name].count_documents({})
            for collection_name in clean_collections
        },
        "quality_issues_found": len(quality_issues),
        "quarantine_records": len(quarantine_records),
    }


if __name__ == "__main__":
    build_clean_collections()
