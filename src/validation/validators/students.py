from typing import Any
from src.validation.validators import ValidatorContext
from src.validation.data_quality_checks import quality_issue
from src.validation.rules import valid_id, normalize_gender, parse_date


def validate_students(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_students.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        student_id = row.get("student_id")
        school_id = row.get("school_id")
        gender = normalize_gender(row.get("gender"))
        enrollment_date = parse_date(row.get("enrollment_date"))
        dropout_date = parse_date(row.get("dropout_date"))
        
        if not valid_id("student_id", student_id):
            issues.append(quality_issue("raw_students", student_id, "invalid_student_id", "high", "student_id", batch_id, school_id))
            continue
        if school_id not in ctx.school_ids:
            issues.append(quality_issue("raw_students", student_id, "invalid_school_relationship", "high", "school_id", batch_id, school_id))
            continue
        if gender is None:
            issues.append(quality_issue("raw_students", student_id, "invalid_gender", "medium", "gender", batch_id, school_id))
            continue
        if enrollment_date is None:
            issues.append(quality_issue("raw_students", student_id, "invalid_enrollment_date", "medium", "enrollment_date", batch_id, school_id))
            continue
        if row.get("status") not in {"Active", "Transferred", "Dropped"}:
            issues.append(quality_issue("raw_students", student_id, "invalid_status", "medium", "status", batch_id, school_id))
            continue
        if row.get("status") == "Dropped" and dropout_date and dropout_date < enrollment_date:
            issues.append(quality_issue("raw_students", student_id, "dropout_before_enrollment", "high", "dropout_date", batch_id, school_id))
            continue
            
        ctx.student_ids.add(student_id)
        clean.append({
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
        })
    return clean, issues
