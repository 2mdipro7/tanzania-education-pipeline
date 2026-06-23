from typing import Any
from src.validation.validators import ValidatorContext
from src.validation.data_quality_checks import quality_issue
from src.validation.rules import valid_id, parse_date


def validate_facilitators(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_facilitators.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        facilitator_id = row.get("facilitator_id")
        
        if not valid_id("facilitator_id", facilitator_id):
            issues.append(quality_issue("raw_facilitators", facilitator_id, "invalid_facilitator_id", "high", "facilitator_id", batch_id))
            continue
            
        ctx.facilitator_ids.add(facilitator_id)
        clean.append({
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
        })
    return clean, issues
