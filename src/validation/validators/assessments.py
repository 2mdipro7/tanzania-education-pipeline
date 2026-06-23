from typing import Any
from src.validation.validators import ValidatorContext
from src.validation.data_quality_checks import quality_issue
from src.validation.rules import valid_id, parse_date, valid_score


def validate_assessments(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_assessments.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        assessment_id = row.get("assessment_id")
        student_id = row.get("student_id")
        school_id = row.get("school_id")
        
        if not valid_id("assessment_id", assessment_id):
            issues.append(quality_issue("raw_assessments", assessment_id, "invalid_assessment_id", "high", "assessment_id", batch_id, school_id))
            continue
        if student_id not in ctx.student_ids:
            issues.append(quality_issue("raw_assessments", assessment_id, "invalid_student_relationship", "high", "student_id", batch_id, school_id))
            continue
        if school_id not in ctx.school_ids:
            issues.append(quality_issue("raw_assessments", assessment_id, "invalid_school_relationship", "high", "school_id", batch_id, school_id))
            continue
        if row.get("assessment_type") not in {"Pre", "Post"}:
            issues.append(quality_issue("raw_assessments", assessment_id, "invalid_assessment_type", "medium", "assessment_type", batch_id, school_id))
            continue
            
        score_fields = [
            "score",
            "score_business",
            "score_financial_literacy",
            "score_communication",
            "score_problem_solving",
        ]
        if any(not valid_score(row.get(field)) for field in score_fields):
            issues.append(quality_issue("raw_assessments", assessment_id, "invalid_score", "high", "score", batch_id, school_id))
            continue
            
        clean.append({
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
        })
    return clean, issues
