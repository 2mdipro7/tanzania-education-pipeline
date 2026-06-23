from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


REFERENCE_DATE = datetime(2026, 7, 20, tzinfo=timezone.utc)


def quality_issue(
    collection: str,
    record_id: str | None,
    issue_type: str,
    severity: str,
    field: str | None,
    batch_id: str | None,
    school_id: str | None = None,
) -> dict[str, Any]:
    return {
        "collection": collection,
        "record_id": record_id,
        "issue_type": issue_type,
        "severity": severity,
        "field": field,
        "batch_id": batch_id,
        "school_id": school_id,
        "detected_at": datetime.now(timezone.utc),
    }


def days_old(value: datetime | None, reference_date: datetime = REFERENCE_DATE) -> int | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return (reference_date - value).days


def ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def run_post_clean_quality_checks(db) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []

    issues.extend(check_source_upload_completeness(db))
    issues.extend(check_source_freshness(db))
    issues.extend(check_device_sync_freshness(db))
    issues.extend(check_school_attendance_support(db))
    issues.extend(check_school_assessment_completion(db))
    issues.extend(check_delivered_sessions_have_attendance(db))
    issues.extend(check_facilitator_caseload(db))

    return issues


def check_source_upload_completeness(db) -> list[dict[str, Any]]:
    issues = []
    for upload in db.source_uploads.find({}, {"_id": 0}):
        source_upload_id = upload.get("source_upload_id")
        batch_id = upload.get("_batch_id")
        expected = upload.get("expected_records") or 0
        loaded = upload.get("loaded_records") or 0
        invalid = upload.get("invalid_records") or 0
        duplicate = upload.get("duplicate_records") or 0

        if loaded < expected:
            issues.append(
                quality_issue(
                    "raw_source_uploads",
                    source_upload_id,
                    "loaded_records_below_expected",
                    "medium",
                    "loaded_records",
                    batch_id,
                )
            )
        if invalid > 0:
            issues.append(
                quality_issue(
                    "raw_source_uploads",
                    source_upload_id,
                    "source_contains_invalid_records",
                    "medium",
                    "invalid_records",
                    batch_id,
                )
            )
        if duplicate > 0:
            issues.append(
                quality_issue(
                    "raw_source_uploads",
                    source_upload_id,
                    "source_contains_duplicate_records",
                    "low",
                    "duplicate_records",
                    batch_id,
                )
            )
    return issues


def check_source_freshness(db) -> list[dict[str, Any]]:
    issues = []
    for upload in db.source_uploads.find({}, {"_id": 0}):
        latest_record_age = days_old(upload.get("latest_record_date"))
        if latest_record_age is None:
            issues.append(
                quality_issue(
                    "raw_source_uploads",
                    upload.get("source_upload_id"),
                    "missing_latest_record_date",
                    "medium",
                    "latest_record_date",
                    upload.get("_batch_id"),
                )
            )
            continue
        if latest_record_age > 3:
            issues.append(
                quality_issue(
                    "raw_source_uploads",
                    upload.get("source_upload_id"),
                    "stale_source_data",
                    "medium" if latest_record_age <= 7 else "high",
                    "latest_record_date",
                    upload.get("_batch_id"),
                )
            )
    return issues


def check_device_sync_freshness(db) -> list[dict[str, Any]]:
    issues = []
    for device in db.field_devices.find({}, {"_id": 0}):
        sync_age = days_old(device.get("last_sync_at"))
        if sync_age is not None and sync_age > 3:
            issues.append(
                quality_issue(
                    "raw_field_devices",
                    device.get("device_id"),
                    "field_device_sync_stale",
                    "medium" if sync_age <= 5 else "high",
                    "last_sync_at",
                    device.get("_batch_id"),
                )
            )
    return issues


def check_school_attendance_support(db) -> list[dict[str, Any]]:
    issues = []
    for school in db.schools.find({}, {"_id": 0, "school_id": 1, "_batch_id": 1}):
        school_id = school["school_id"]
        attendance_count = db.attendance.count_documents({"school_id": school_id})
        attended_count = db.attendance.count_documents({"school_id": school_id, "attended": True})
        attendance_rate = ratio(attended_count, attendance_count)
        open_interventions = db.interventions.count_documents(
            {
                "school_id": school_id,
                "status": {"$in": ["Open", "In Progress", "Overdue"]},
            }
        )
        if attendance_rate is not None and attendance_rate < 0.68 and open_interventions == 0:
            issues.append(
                quality_issue(
                    "raw_schools",
                    school_id,
                    "low_attendance_without_open_intervention",
                    "high",
                    "attendance",
                    school.get("_batch_id"),
                    school_id,
                )
            )
    return issues


def check_school_assessment_completion(db) -> list[dict[str, Any]]:
    issues = []
    for school in db.schools.find({}, {"_id": 0, "school_id": 1, "_batch_id": 1}):
        school_id = school["school_id"]
        active_student_ids = [
            student["student_id"]
            for student in db.students.find(
                {"school_id": school_id, "status": "Active"},
                {"_id": 0, "student_id": 1},
            )
        ]
        if not active_student_ids:
            continue
        post_student_ids = set(
            assessment["student_id"]
            for assessment in db.assessments.find(
                {
                    "school_id": school_id,
                    "assessment_type": "Post",
                    "student_id": {"$in": active_student_ids},
                },
                {"_id": 0, "student_id": 1},
            )
        )
        completion_rate = ratio(len(post_student_ids), len(active_student_ids))
        if completion_rate is not None and completion_rate < 0.70:
            issues.append(
                quality_issue(
                    "raw_schools",
                    school_id,
                    "low_post_assessment_completion",
                    "medium",
                    "assessments",
                    school.get("_batch_id"),
                    school_id,
                )
            )
    return issues


def check_delivered_sessions_have_attendance(db) -> list[dict[str, Any]]:
    issues = []
    delivered_sessions = db.sessions.find(
        {"delivery_status": "Delivered"},
        {"_id": 0, "session_id": 1, "school_id": 1, "_batch_id": 1},
    )
    for session in delivered_sessions:
        attendance_count = db.attendance.count_documents({"session_id": session["session_id"]})
        if attendance_count == 0:
            issues.append(
                quality_issue(
                    "raw_sessions",
                    session["session_id"],
                    "delivered_session_without_attendance",
                    "high",
                    "attendance",
                    session.get("_batch_id"),
                    session.get("school_id"),
                )
            )
    return issues


def check_facilitator_caseload(db) -> list[dict[str, Any]]:
    issues = []
    for facilitator in db.facilitators.find({}, {"_id": 0}):
        caseload = facilitator.get("caseload_school_count") or 0
        if caseload > 5:
            issues.append(
                quality_issue(
                    "raw_facilitators",
                    facilitator.get("facilitator_id"),
                    "facilitator_caseload_above_threshold",
                    "low",
                    "caseload_school_count",
                    facilitator.get("_batch_id"),
                )
            )
    return issues
