from typing import Any
from src.validation.validators import ValidatorContext
from src.validation.data_quality_checks import quality_issue
from src.validation.rules import valid_id, parse_date


def validate_sessions(db: Any, ctx: ValidatorContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean = []
    issues = []
    for row in db.raw_sessions.find({}, {"_id": 0}):
        batch_id = row.get("_batch_id")
        session_id = row.get("session_id")
        school_id = row.get("school_id")
        module_id = row.get("module_id")
        facilitator_id = row.get("facilitator_id")
        planned_date = parse_date(row.get("planned_date"))
        delivered_date = parse_date(row.get("delivered_date"))
        
        if not valid_id("session_id", session_id):
            issues.append(quality_issue("raw_sessions", session_id, "invalid_session_id", "high", "session_id", batch_id, school_id))
            continue
        if school_id not in ctx.school_ids:
            issues.append(quality_issue("raw_sessions", session_id, "invalid_school_relationship", "high", "school_id", batch_id, school_id))
            continue
        if module_id not in ctx.module_ids:
            issues.append(quality_issue("raw_sessions", session_id, "invalid_module_relationship", "high", "module_id", batch_id, school_id))
            continue
        if facilitator_id not in ctx.facilitator_ids:
            issues.append(quality_issue("raw_sessions", session_id, "invalid_facilitator_relationship", "medium", "facilitator_id", batch_id, school_id))
            continue
        if planned_date is None:
            issues.append(quality_issue("raw_sessions", session_id, "invalid_planned_date", "medium", "planned_date", batch_id, school_id))
            continue
        if delivered_date and delivered_date < planned_date:
            issues.append(quality_issue("raw_sessions", session_id, "delivered_before_planned", "medium", "delivered_date", batch_id, school_id))
            continue
            
        ctx.session_ids.add(session_id)
        ctx.session_school_lookup[session_id] = school_id
        clean.append({
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
        })
    return clean, issues
