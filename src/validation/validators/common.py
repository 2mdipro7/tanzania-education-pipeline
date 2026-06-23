from typing import Any
from src.validation.validators import ValidatorContext
from src.validation.data_quality_checks import quality_issue
from src.validation.rules import valid_id, parse_date


def validate_data_collectors(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_data_collectors.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        collector_id = row.get("collector_id")
        if not valid_id("collector_id", collector_id):
            issues.append(quality_issue("raw_data_collectors", collector_id, "invalid_collector_id", "high", "collector_id", batch_id))
            continue
        ctx.collector_ids.add(collector_id)
        clean.append({
            "collector_id": collector_id,
            "full_name": row.get("full_name"),
            "role": row.get("role"),
            "assigned_region": row.get("assigned_region"),
            "assigned_district": row.get("assigned_district"),
            "phone": row.get("phone"),
            "supervisor_id": row.get("supervisor_id"),
            "active": bool(row.get("active")),
            "_batch_id": batch_id,
        })
    return clean, issues


def validate_field_devices(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_field_devices.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        device_id = row.get("device_id")
        collector_id = row.get("assigned_to")
        if not valid_id("device_id", device_id):
            issues.append(quality_issue("raw_field_devices", device_id, "invalid_device_id", "high", "device_id", batch_id))
            continue
        if collector_id not in ctx.collector_ids:
            issues.append(quality_issue("raw_field_devices", device_id, "invalid_collector_relationship", "medium", "assigned_to", batch_id))
            continue
        ctx.device_ids.add(device_id)
        clean.append({
            "device_id": device_id,
            "assigned_to": collector_id,
            "assigned_region": row.get("assigned_region"),
            "assigned_district": row.get("assigned_district"),
            "device_model": row.get("device_model"),
            "os_version": row.get("os_version"),
            "connectivity_quality": row.get("connectivity_quality"),
            "last_sync_at": parse_date(row.get("last_sync_at")),
            "battery_health": row.get("battery_health"),
            "app_version": row.get("app_version"),
            "_batch_id": batch_id,
        })
    return clean, issues


def validate_curriculum_modules(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_curriculum_modules.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        module_id = row.get("module_id")
        if not valid_id("module_id", module_id):
            issues.append(quality_issue("raw_curriculum_modules", module_id, "invalid_module_id", "high", "module_id", batch_id))
            continue
        ctx.module_ids.add(module_id)
        clean.append({
            "module_id": module_id,
            "module_name": row.get("module_name"),
            "term": row.get("term"),
            "week_number": row.get("week_number"),
            "competency_area": row.get("competency_area"),
            "expected_duration_minutes": row.get("expected_duration_minutes"),
            "required_materials": row.get("required_materials") or [],
            "is_core_module": bool(row.get("is_core_module")),
            "prerequisite_module_id": row.get("prerequisite_module_id"),
            "_batch_id": batch_id,
        })
    return clean, issues


def validate_facilitator_visits(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_facilitator_visits.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        visit_id = row.get("visit_id")
        school_id = row.get("school_id")
        facilitator_id = row.get("facilitator_id")
        planned_date = parse_date(row.get("planned_date"))
        completed_date = parse_date(row.get("completed_date"))
        if not valid_id("visit_id", visit_id):
            issues.append(quality_issue("raw_facilitator_visits", visit_id, "invalid_visit_id", "high", "visit_id", batch_id, school_id))
            continue
        if school_id not in ctx.school_ids:
            issues.append(quality_issue("raw_facilitator_visits", visit_id, "invalid_school_relationship", "high", "school_id", batch_id, school_id))
            continue
        if facilitator_id not in ctx.facilitator_ids:
            issues.append(quality_issue("raw_facilitator_visits", visit_id, "invalid_facilitator_relationship", "medium", "facilitator_id", batch_id, school_id))
            continue
        if planned_date is None:
            issues.append(quality_issue("raw_facilitator_visits", visit_id, "invalid_planned_date", "medium", "planned_date", batch_id, school_id))
            continue
        clean.append({
            "visit_id": visit_id,
            "school_id": school_id,
            "facilitator_id": facilitator_id,
            "visit_type": row.get("visit_type"),
            "planned_date": planned_date,
            "completed_date": completed_date,
            "duration_minutes": row.get("duration_minutes"),
            "visit_status": "Completed" if completed_date else "Missed",
            "quality_issues_found": row.get("quality_issues_found") or [],
            "coaching_score": row.get("coaching_score"),
            "follow_up_required": bool(row.get("follow_up_required")),
            "follow_up_due_date": parse_date(row.get("follow_up_due_date")),
            "notes": row.get("notes"),
            "_batch_id": batch_id,
        })
    return clean, issues


def validate_student_surveys(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_student_surveys.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        survey_id = row.get("survey_id")
        student_id = row.get("student_id")
        school_id = row.get("school_id")
        if not valid_id("survey_id", survey_id):
            issues.append(quality_issue("raw_student_surveys", survey_id, "invalid_survey_id", "high", "survey_id", batch_id, school_id))
            continue
        if student_id not in ctx.student_ids:
            issues.append(quality_issue("raw_student_surveys", survey_id, "invalid_student_relationship", "high", "student_id", batch_id, school_id))
            continue
        clean.append({
            "survey_id": survey_id,
            "student_id": student_id,
            "school_id": school_id,
            "term": row.get("term"),
            "survey_date": parse_date(row.get("survey_date")),
            "confidence_score": row.get("confidence_score"),
            "entrepreneurship_interest": row.get("entrepreneurship_interest"),
            "financial_confidence": row.get("financial_confidence"),
            "teamwork_confidence": row.get("teamwork_confidence"),
            "satisfaction_score": row.get("satisfaction_score"),
            "would_recommend_program": bool(row.get("would_recommend_program")),
            "open_feedback": row.get("open_feedback"),
            "recorded_by": row.get("recorded_by"),
            "source_device_id": row.get("source_device_id"),
            "_batch_id": batch_id,
        })
    return clean, issues


def validate_program_targets(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_program_targets.find({}, {"_id": 0}):
        clean.append({
            "target_id": row.get("target_id"),
            "region": row.get("region"),
            "district": row.get("district"),
            "term": row.get("term"),
            "target_students": row.get("target_students"),
            "target_active_students": row.get("target_active_students"),
            "target_sessions": row.get("target_sessions"),
            "target_attendance_rate": row.get("target_attendance_rate"),
            "target_assessment_completion_rate": row.get("target_assessment_completion_rate"),
            "target_visit_completion_rate": row.get("target_visit_completion_rate"),
            "_batch_id": row.get("_batch_id"),
        })
    return clean, issues


def validate_source_uploads(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_source_uploads.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        source_upload_id = row.get("source_upload_id")
        if not valid_id("source_upload_id", source_upload_id):
            issues.append(quality_issue("raw_source_uploads", source_upload_id, "invalid_source_upload_id", "medium", "source_upload_id", batch_id))
            continue
        clean.append({
            "source_upload_id": source_upload_id,
            "source_name": row.get("source_name"),
            "source_file": row.get("source_file"),
            "uploaded_by": row.get("uploaded_by"),
            "uploaded_at": parse_date(row.get("uploaded_at")),
            "expected_records": row.get("expected_records"),
            "loaded_records": row.get("loaded_records"),
            "valid_records": row.get("valid_records"),
            "invalid_records": row.get("invalid_records"),
            "duplicate_records": row.get("duplicate_records"),
            "latest_record_date": parse_date(row.get("latest_record_date")),
            "pipeline_status": row.get("pipeline_status"),
            "source_device_id": row.get("source_device_id"),
            "connectivity_quality": row.get("connectivity_quality"),
            "_batch_id": batch_id,
        })
    return clean, issues


def validate_interventions(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_interventions.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        intervention_id = row.get("intervention_id")
        school_id = row.get("school_id")
        student_id = row.get("student_id")
        if not valid_id("intervention_id", intervention_id):
            issues.append(quality_issue("raw_interventions", intervention_id, "invalid_intervention_id", "medium", "intervention_id", batch_id, school_id))
            continue
        if school_id not in ctx.school_ids:
            issues.append(quality_issue("raw_interventions", intervention_id, "invalid_school_relationship", "high", "school_id", batch_id, school_id))
            continue
        if student_id and student_id not in ctx.student_ids:
            issues.append(quality_issue("raw_interventions", intervention_id, "invalid_student_relationship", "medium", "student_id", batch_id, school_id))
            continue
        clean.append({
            "intervention_id": intervention_id,
            "school_id": school_id,
            "student_id": student_id,
            "intervention_type": row.get("intervention_type"),
            "trigger_reason": row.get("trigger_reason"),
            "assigned_to": row.get("assigned_to"),
            "opened_date": parse_date(row.get("opened_date")),
            "due_date": parse_date(row.get("due_date")),
            "closed_date": parse_date(row.get("closed_date")),
            "status": row.get("status"),
            "outcome": row.get("outcome"),
            "priority": row.get("priority"),
            "_batch_id": batch_id,
        })
    return clean, issues
