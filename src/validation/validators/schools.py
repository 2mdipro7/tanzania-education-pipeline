from typing import Any
from src.validation.validators import ValidatorContext
from src.validation.data_quality_checks import quality_issue
from src.validation.rules import valid_id


def is_number(val: Any) -> bool:
    return isinstance(val, (int, float))


def validate_schools(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_schools.find({}, {"_id": 0}):
        school_id = row.get("school_id")
        batch_id = row.get("_batch_id")
        latitude = row.get("latitude")
        longitude = row.get("longitude")
        
        if not valid_id("school_id", school_id):
            issues.append(quality_issue("raw_schools", school_id, "invalid_school_id", "high", "school_id", batch_id))
            continue
        if not row.get("school_name") or not row.get("region") or not row.get("district"):
            issues.append(quality_issue("raw_schools", school_id, "missing_required_field", "high", None, batch_id, school_id))
            continue
        if not is_number(latitude) or not is_number(longitude) or not (-12 <= latitude <= 0) or not (28 <= longitude <= 42):
            issues.append(quality_issue("raw_schools", school_id, "invalid_geolocation", "high", "latitude/longitude", batch_id, school_id))
            continue
            
        ctx.school_ids.add(school_id)
        clean.append({
            "school_id": school_id,
            "school_name": row.get("school_name"),
            "region": row.get("region"),
            "district": row.get("district"),
            "ward": row.get("ward"),
            "street_address": row.get("street_address"),
            "facilitator_id": row.get("facilitator_id"),
            "location": row.get("location"),
            "latitude": latitude,
            "longitude": longitude,
            "implementation_status": row.get("implementation_status"),
            "infrastructure_rating": row.get("infrastructure_rating"),
        })
    return clean, issues
