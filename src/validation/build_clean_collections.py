from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.db import get_database
from src.validation.data_quality_checks import run_post_clean_quality_checks
from src.validation.rules import normalize_gender, parse_date, valid_id, valid_score


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


def issue(
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


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float))


def build_clean_collections() -> dict[str, Any]:
    db = get_database()
    issues: list[dict[str, Any]] = []

    schools = []
    school_ids = set()
    for row in db.raw_schools.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        school_id = row.get("school_id")
        latitude = row.get("latitude")
        longitude = row.get("longitude")
        if not valid_id("school_id", school_id):
            issues.append(issue("raw_schools", school_id, "invalid_school_id", "high", "school_id", batch_id))
            continue
        if not row.get("school_name") or not row.get("region") or not row.get("district"):
            issues.append(issue("raw_schools", school_id, "missing_required_field", "high", None, batch_id, school_id))
            continue
        if not is_number(latitude) or not is_number(longitude) or not (-12 <= latitude <= 0) or not (28 <= longitude <= 42):
            issues.append(issue("raw_schools", school_id, "invalid_geolocation", "high", "latitude/longitude", batch_id, school_id))
            continue
        school_ids.add(school_id)
        schools.append(
            {
                "school_id": school_id,
                "school_name": row["school_name"],
                "region": row["region"],
                "district": row["district"],
                "ward": row.get("ward") or "Unknown",
                "street_address": row.get("street_address"),
                "postal_code": row.get("postal_code"),
                "latitude": latitude,
                "longitude": longitude,
                "location": row.get("location") or {"type": "Point", "coordinates": [longitude, latitude]},
                "school_type": row.get("school_type") or "Unknown",
                "urban_rural": row.get("urban_rural") or "Unknown",
                "ownership": row.get("ownership") or "Unknown",
                "head_teacher_name": row.get("head_teacher_name"),
                "head_teacher_phone": row.get("head_teacher_phone"),
                "student_capacity": row.get("student_capacity"),
                "number_of_teachers": row.get("number_of_teachers"),
                "electricity_available": bool(row.get("electricity_available")),
                "internet_available": bool(row.get("internet_available")),
                "has_projector": bool(row.get("has_projector")),
                "has_library": bool(row.get("has_library")),
                "water_access": row.get("water_access"),
                "program_start_date": parse_date(row.get("program_start_date")),
                "implementation_status": row.get("implementation_status") or "Unknown",
                "school_context_risk": row.get("school_context_risk"),
                "facilitator_id": row.get("facilitator_id"),
                "_batch_id": batch_id,
            }
        )

    replace_collection(db, "schools", schools)

    facilitators = []
    facilitator_ids = set()
    for row in db.raw_facilitators.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        facilitator_id = row.get("facilitator_id")
        if not valid_id("facilitator_id", facilitator_id):
            issues.append(issue("raw_facilitators", facilitator_id, "invalid_facilitator_id", "high", "facilitator_id", batch_id))
            continue
        facilitator_ids.add(facilitator_id)
        facilitators.append(
            {
                "facilitator_id": facilitator_id,
                "full_name": row.get("full_name"),
                "region": row.get("region"),
                "primary_district": row.get("primary_district"),
                "assigned_districts": row.get("assigned_districts") or [],
                "phone": row.get("phone"),
                "email": row.get("email"),
                "hire_date": parse_date(row.get("hire_date")),
                "status": row.get("status"),
                "supervisor_id": row.get("supervisor_id"),
                "caseload_school_count": row.get("caseload_school_count"),
                "home_base_latitude": row.get("home_base_latitude"),
                "home_base_longitude": row.get("home_base_longitude"),
                "_batch_id": batch_id,
            }
        )

    replace_collection(db, "facilitators", facilitators)

    data_collectors = []
    collector_ids = set()
    for row in db.raw_data_collectors.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        collector_id = row.get("collector_id")
        if not valid_id("collector_id", collector_id):
            issues.append(issue("raw_data_collectors", collector_id, "invalid_collector_id", "high", "collector_id", batch_id))
            continue
        collector_ids.add(collector_id)
        data_collectors.append(
            {
                "collector_id": collector_id,
                "full_name": row.get("full_name"),
                "role": row.get("role"),
                "assigned_region": row.get("assigned_region"),
                "assigned_district": row.get("assigned_district"),
                "phone": row.get("phone"),
                "supervisor_id": row.get("supervisor_id"),
                "active": bool(row.get("active")),
                "_batch_id": batch_id,
            }
        )

    replace_collection(db, "data_collectors", data_collectors)

    field_devices = []
    device_ids = set()
    for row in db.raw_field_devices.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        device_id = row.get("device_id")
        collector_id = row.get("assigned_to")
        if not valid_id("device_id", device_id):
            issues.append(issue("raw_field_devices", device_id, "invalid_device_id", "high", "device_id", batch_id))
            continue
        if collector_id not in collector_ids:
            issues.append(issue("raw_field_devices", device_id, "invalid_collector_relationship", "medium", "assigned_to", batch_id))
            continue
        device_ids.add(device_id)
        field_devices.append(
            {
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
            }
        )

    replace_collection(db, "field_devices", field_devices)

    curriculum_modules = []
    module_ids = set()
    for row in db.raw_curriculum_modules.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        module_id = row.get("module_id")
        if not valid_id("module_id", module_id):
            issues.append(issue("raw_curriculum_modules", module_id, "invalid_module_id", "high", "module_id", batch_id))
            continue
        module_ids.add(module_id)
        curriculum_modules.append(
            {
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
            }
        )

    replace_collection(db, "curriculum_modules", curriculum_modules)

    students = []
    student_ids = set()
    for row in db.raw_students.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        student_id = row.get("student_id")
        school_id = row.get("school_id")
        gender = normalize_gender(row.get("gender"))
        enrollment_date = parse_date(row.get("enrollment_date"))
        dropout_date = parse_date(row.get("dropout_date"))
        if not valid_id("student_id", student_id):
            issues.append(issue("raw_students", student_id, "invalid_student_id", "high", "student_id", batch_id, school_id))
            continue
        if school_id not in school_ids:
            issues.append(issue("raw_students", student_id, "invalid_school_relationship", "high", "school_id", batch_id, school_id))
            continue
        if gender is None:
            issues.append(issue("raw_students", student_id, "invalid_gender", "medium", "gender", batch_id, school_id))
            continue
        if enrollment_date is None:
            issues.append(issue("raw_students", student_id, "invalid_enrollment_date", "medium", "enrollment_date", batch_id, school_id))
            continue
        if row.get("status") not in {"Active", "Transferred", "Dropped"}:
            issues.append(issue("raw_students", student_id, "invalid_status", "medium", "status", batch_id, school_id))
            continue
        if row.get("status") == "Dropped" and dropout_date and dropout_date < enrollment_date:
            issues.append(issue("raw_students", student_id, "dropout_before_enrollment", "high", "dropout_date", batch_id, school_id))
            continue
        student_ids.add(student_id)
        students.append(
            {
                "student_id": student_id,
                "school_id": school_id,
                "first_name": row.get("first_name"),
                "last_name": row.get("last_name"),
                "gender": gender,
                "age": row.get("age"),
                "date_of_birth": parse_date(row.get("date_of_birth")),
                "class_level": row.get("class_level"),
                "stream": row.get("stream"),
                "guardian_occupation": row.get("guardian_occupation"),
                "household_size": row.get("household_size"),
                "has_phone_access": bool(row.get("has_phone_access")),
                "distance_to_school_km": row.get("distance_to_school_km"),
                "transport_mode": row.get("transport_mode"),
                "disability_status": row.get("disability_status"),
                "baseline_confidence_score": row.get("baseline_confidence_score"),
                "baseline_risk_level": row.get("baseline_risk_level"),
                "enrollment_date": enrollment_date,
                "status": row.get("status"),
                "dropout_date": dropout_date,
                "dropout_reason": row.get("dropout_reason"),
                "transfer_school_id": row.get("transfer_school_id"),
                "program_cohort": row.get("program_cohort"),
                "_batch_id": batch_id,
            }
        )

    replace_collection(db, "students", students)

    sessions = []
    session_ids = set()
    session_school_lookup = {}
    for row in db.raw_sessions.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        session_id = row.get("session_id")
        school_id = row.get("school_id")
        module_id = row.get("module_id")
        facilitator_id = row.get("facilitator_id")
        planned_date = parse_date(row.get("planned_date"))
        delivered_date = parse_date(row.get("delivered_date"))
        if not valid_id("session_id", session_id):
            issues.append(issue("raw_sessions", session_id, "invalid_session_id", "high", "session_id", batch_id, school_id))
            continue
        if school_id not in school_ids:
            issues.append(issue("raw_sessions", session_id, "invalid_school_relationship", "high", "school_id", batch_id, school_id))
            continue
        if module_id not in module_ids:
            issues.append(issue("raw_sessions", session_id, "invalid_module_relationship", "high", "module_id", batch_id, school_id))
            continue
        if facilitator_id not in facilitator_ids:
            issues.append(issue("raw_sessions", session_id, "invalid_facilitator_relationship", "medium", "facilitator_id", batch_id, school_id))
            continue
        if planned_date is None:
            issues.append(issue("raw_sessions", session_id, "invalid_planned_date", "medium", "planned_date", batch_id, school_id))
            continue
        if delivered_date and delivered_date < planned_date:
            issues.append(issue("raw_sessions", session_id, "delivered_before_planned", "medium", "delivered_date", batch_id, school_id))
            continue
        session_ids.add(session_id)
        session_school_lookup[session_id] = school_id
        sessions.append(
            {
                "session_id": session_id,
                "school_id": school_id,
                "facilitator_id": facilitator_id,
                "module_id": module_id,
                "module_name": row.get("module_name"),
                "competency_area": row.get("competency_area"),
                "term": row.get("term"),
                "planned_date": planned_date,
                "delivered_date": delivered_date,
                "delivery_status": "Delivered" if delivered_date else "Planned",
                "delivery_mode": row.get("delivery_mode"),
                "duration_minutes": row.get("duration_minutes"),
                "delivery_quality_score": row.get("delivery_quality_score"),
                "materials_available": bool(row.get("materials_available")),
                "_batch_id": batch_id,
            }
        )

    replace_collection(db, "sessions", sessions)

    attendance = []
    seen_attendance_keys = set()
    for row in db.raw_attendance.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        attendance_id = row.get("attendance_id")
        student_id = row.get("student_id")
        session_id = row.get("session_id")
        school_id = session_school_lookup.get(session_id) or row.get("school_id")
        if not valid_id("attendance_id", attendance_id):
            issues.append(issue("raw_attendance", attendance_id, "invalid_attendance_id", "high", "attendance_id", batch_id, school_id))
            continue
        if student_id not in student_ids:
            issues.append(issue("raw_attendance", attendance_id, "invalid_student_relationship", "high", "student_id", batch_id, school_id))
            continue
        if session_id not in session_ids:
            issues.append(issue("raw_attendance", attendance_id, "invalid_session_relationship", "high", "session_id", batch_id, school_id))
            continue
        if row.get("recorded_by") not in collector_ids:
            issues.append(issue("raw_attendance", attendance_id, "invalid_collector_relationship", "medium", "recorded_by", batch_id, school_id))
            continue
        if row.get("source_device_id") not in device_ids:
            issues.append(issue("raw_attendance", attendance_id, "invalid_device_relationship", "medium", "source_device_id", batch_id, school_id))
            continue
        key = (student_id, session_id)
        if key in seen_attendance_keys:
            issues.append(issue("raw_attendance", attendance_id, "duplicate_attendance_record", "medium", None, batch_id, school_id))
            continue
        seen_attendance_keys.add(key)
        attendance.append(
            {
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
            }
        )

    replace_collection(db, "attendance", attendance)

    assessments = []
    for row in db.raw_assessments.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        assessment_id = row.get("assessment_id")
        student_id = row.get("student_id")
        school_id = row.get("school_id")
        if not valid_id("assessment_id", assessment_id):
            issues.append(issue("raw_assessments", assessment_id, "invalid_assessment_id", "high", "assessment_id", batch_id, school_id))
            continue
        if student_id not in student_ids:
            issues.append(issue("raw_assessments", assessment_id, "invalid_student_relationship", "high", "student_id", batch_id, school_id))
            continue
        if school_id not in school_ids:
            issues.append(issue("raw_assessments", assessment_id, "invalid_school_relationship", "high", "school_id", batch_id, school_id))
            continue
        if row.get("assessment_type") not in {"Pre", "Post"}:
            issues.append(issue("raw_assessments", assessment_id, "invalid_assessment_type", "medium", "assessment_type", batch_id, school_id))
            continue
        score_fields = [
            "score",
            "score_business",
            "score_financial_literacy",
            "score_communication",
            "score_problem_solving",
        ]
        if any(not valid_score(row.get(field)) for field in score_fields):
            issues.append(issue("raw_assessments", assessment_id, "invalid_score", "high", "score", batch_id, school_id))
            continue
        assessments.append(
            {
                "assessment_id": assessment_id,
                "student_id": student_id,
                "school_id": school_id,
                "assessment_type": row.get("assessment_type"),
                "term": row.get("term"),
                "score": row.get("score"),
                "score_business": row.get("score_business"),
                "score_financial_literacy": row.get("score_financial_literacy"),
                "score_communication": row.get("score_communication"),
                "score_problem_solving": row.get("score_problem_solving"),
                "max_score": row.get("max_score"),
                "assessment_date": parse_date(row.get("assessment_date")),
                "assessor_id": row.get("assessor_id"),
                "source_device_id": row.get("source_device_id"),
                "submission_source": row.get("submission_source"),
                "_batch_id": batch_id,
            }
        )

    replace_collection(db, "assessments", assessments)

    visits = []
    for row in db.raw_facilitator_visits.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        visit_id = row.get("visit_id")
        school_id = row.get("school_id")
        facilitator_id = row.get("facilitator_id")
        planned_date = parse_date(row.get("planned_date"))
        completed_date = parse_date(row.get("completed_date"))
        if not valid_id("visit_id", visit_id):
            issues.append(issue("raw_facilitator_visits", visit_id, "invalid_visit_id", "high", "visit_id", batch_id, school_id))
            continue
        if school_id not in school_ids:
            issues.append(issue("raw_facilitator_visits", visit_id, "invalid_school_relationship", "high", "school_id", batch_id, school_id))
            continue
        if facilitator_id not in facilitator_ids:
            issues.append(issue("raw_facilitator_visits", visit_id, "invalid_facilitator_relationship", "medium", "facilitator_id", batch_id, school_id))
            continue
        if planned_date is None:
            issues.append(issue("raw_facilitator_visits", visit_id, "invalid_planned_date", "medium", "planned_date", batch_id, school_id))
            continue
        visits.append(
            {
                "visit_id": visit_id,
                "school_id": school_id,
                "facilitator_id": facilitator_id,
                "visit_type": row.get("visit_type"),
                "planned_date": planned_date,
                "completed_date": completed_date,
                "duration_minutes": row.get("duration_minutes"),
                "visit_status": "Completed" if completed_date else "Missed",
                "issues_found": row.get("issues_found") or [],
                "coaching_score": row.get("coaching_score"),
                "follow_up_required": bool(row.get("follow_up_required")),
                "follow_up_due_date": parse_date(row.get("follow_up_due_date")),
                "notes": row.get("notes"),
                "_batch_id": batch_id,
            }
        )

    replace_collection(db, "facilitator_visits", visits)

    student_surveys = []
    for row in db.raw_student_surveys.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        survey_id = row.get("survey_id")
        student_id = row.get("student_id")
        school_id = row.get("school_id")
        if not valid_id("survey_id", survey_id):
            issues.append(issue("raw_student_surveys", survey_id, "invalid_survey_id", "high", "survey_id", batch_id, school_id))
            continue
        if student_id not in student_ids:
            issues.append(issue("raw_student_surveys", survey_id, "invalid_student_relationship", "high", "student_id", batch_id, school_id))
            continue
        student_surveys.append(
            {
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
            }
        )

    replace_collection(db, "student_surveys", student_surveys)

    targets = []
    for row in db.raw_program_targets.find({}, {"_id": 0}):
        targets.append(
            {
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
            }
        )

    replace_collection(db, "program_targets", targets)

    source_uploads = []
    for row in db.raw_source_uploads.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        source_upload_id = row.get("source_upload_id")
        if not valid_id("source_upload_id", source_upload_id):
            issues.append(issue("raw_source_uploads", source_upload_id, "invalid_source_upload_id", "medium", "source_upload_id", batch_id))
            continue
        source_uploads.append(
            {
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
            }
        )

    replace_collection(db, "source_uploads", source_uploads)

    interventions = []
    for row in db.raw_interventions.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        intervention_id = row.get("intervention_id")
        school_id = row.get("school_id")
        student_id = row.get("student_id")
        if not valid_id("intervention_id", intervention_id):
            issues.append(issue("raw_interventions", intervention_id, "invalid_intervention_id", "medium", "intervention_id", batch_id, school_id))
            continue
        if school_id not in school_ids:
            issues.append(issue("raw_interventions", intervention_id, "invalid_school_relationship", "high", "school_id", batch_id, school_id))
            continue
        if student_id and student_id not in student_ids:
            issues.append(issue("raw_interventions", intervention_id, "invalid_student_relationship", "medium", "student_id", batch_id, school_id))
            continue
        interventions.append(
            {
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
            }
        )

    replace_collection(db, "interventions", interventions)
    issues.extend(run_post_clean_quality_checks(db))
    quarantine_records = build_quarantine_records(db, issues)
    replace_collection(db, "quality_issues", issues)
    replace_collection(db, "quarantine_records", quarantine_records)
    print(f"Cleaned collections and logged {len(issues)} quality issues")
    clean_collections = [
        "schools",
        "facilitators",
        "data_collectors",
        "field_devices",
        "curriculum_modules",
        "students",
        "sessions",
        "attendance",
        "assessments",
        "facilitator_visits",
        "student_surveys",
        "program_targets",
        "source_uploads",
        "interventions",
    ]
    return {
        "clean_counts": {
            collection_name: db[collection_name].count_documents({})
            for collection_name in clean_collections
        },
        "quality_issues_found": len(issues),
        "quarantine_records": len(quarantine_records),
    }


if __name__ == "__main__":
    build_clean_collections()
