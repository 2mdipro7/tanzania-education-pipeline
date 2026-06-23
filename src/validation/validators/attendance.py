from typing import Any
from src.validation.validators import ValidatorContext
from src.validation.data_quality_checks import quality_issue
from src.validation.rules import valid_id, parse_date


def validate_attendance(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_attendance.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        attendance_id = row.get("attendance_id")
        student_id = row.get("student_id")
        session_id = row.get("session_id")
        school_id = ctx.session_school_lookup.get(session_id) or row.get("school_id")
        
        if not valid_id("attendance_id", attendance_id):
            issues.append(quality_issue("raw_attendance", attendance_id, "invalid_attendance_id", "high", "attendance_id", batch_id, school_id))
            continue
        if student_id not in ctx.student_ids:
            issues.append(quality_issue("raw_attendance", attendance_id, "invalid_student_relationship", "high", "student_id", batch_id, school_id))
            continue
        if session_id not in ctx.session_ids:
            issues.append(quality_issue("raw_attendance", attendance_id, "invalid_session_relationship", "high", "session_id", batch_id, school_id))
            continue
        if row.get("recorded_by") not in ctx.collector_ids:
            issues.append(quality_issue("raw_attendance", attendance_id, "invalid_collector_relationship", "medium", "recorded_by", batch_id, school_id))
            continue
        if row.get("source_device_id") not in ctx.device_ids:
            issues.append(quality_issue("raw_attendance", attendance_id, "invalid_device_relationship", "medium", "source_device_id", batch_id, school_id))
            continue
            
        key = (student_id, session_id)
        if key in ctx.seen_attendance_keys:
            issues.append(quality_issue("raw_attendance", attendance_id, "duplicate_attendance_record", "medium", None, batch_id, school_id))
            continue
        ctx.seen_attendance_keys.add(key)
        
        clean.append({
            "attendance_id": attendance_id,
            "student_id": student_id,
            "session_id": session_id,
            "school_id": school_id,
            "attendance_date": parse_date(row.get("attendance_date")),
            "attended": bool(row.get("attended")),
            "arrival_status": row.get("arrival_status"),
            "minutes_late": row.get("minutes_late") or 0,
            "absence_reason": row.get("absence_reason"),
            "recorded_by": row.get("recorded_by"),
            "source_device_id": row.get("source_device_id"),
            "recorded_at": parse_date(row.get("recorded_at")),
            "is_late_submission": bool(row.get("is_late_submission")),
            "upload_delay_days": row.get("upload_delay_days") or 0,
            "submission_channel": row.get("submission_channel"),
            "_batch_id": batch_id,
        })
    return clean, issues
