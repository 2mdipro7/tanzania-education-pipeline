from __future__ import annotations

from typing import Any

from src.db import get_database


MART_CONTRACTS: dict[str, dict[str, Any]] = {
    "mart_school_performance": {
        "primary_key": ["school_id"],
        "required_fields": [
            "school_id",
            "school_name",
            "region",
            "district",
            "latitude",
            "longitude",
            "location",
            "active_students",
            "attendance_rate",
            "session_delivery_rate",
            "assessment_completion_rate",
            "late_submission_rate",
            "risk_status",
        ],
        "rate_fields": [
            "attendance_rate",
            "session_delivery_rate",
            "assessment_completion_rate",
            "facilitator_visit_completion_rate",
            "late_submission_rate",
        ],
        "geojson_field": "location",
    },
    "mart_regional_summary": {
        "primary_key": ["region", "district"],
        "required_fields": [
            "region",
            "district",
            "schools",
            "active_students",
            "avg_attendance_rate",
            "avg_session_delivery_rate",
            "avg_assessment_completion_rate",
            "avg_late_submission_rate",
            "at_risk_schools",
        ],
        "rate_fields": [
            "avg_attendance_rate",
            "avg_session_delivery_rate",
            "avg_assessment_completion_rate",
            "avg_late_submission_rate",
        ],
    },
    "mart_term2_overview": {
        "primary_key": ["term"],
        "required_fields": [
            "term",
            "schools",
            "active_students",
            "avg_attendance_rate",
            "avg_session_delivery_rate",
            "avg_assessment_completion_rate",
            "avg_late_submission_rate",
            "at_risk_schools",
            "data_quality_issues",
        ],
        "rate_fields": [
            "avg_attendance_rate",
            "avg_session_delivery_rate",
            "avg_assessment_completion_rate",
            "avg_facilitator_visit_completion_rate",
            "avg_late_submission_rate",
        ],
    },
    "mart_data_quality": {
        "primary_key": ["collection", "issue_type", "severity"],
        "required_fields": [
            "collection",
            "issue_type",
            "severity",
            "issue_count",
        ],
        "rate_fields": [],
    },
}


def duplicate_key_pipeline(primary_key: list[str]) -> list[dict[str, Any]]:
    group_id = {field: f"${field}" for field in primary_key}
    return [
        {"$group": {"_id": group_id, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$limit": 1},
    ]


def validate_mart_contracts(raise_on_error: bool = True) -> dict[str, Any]:
    db = get_database()
    errors: list[dict[str, Any]] = []
    checks_run = 0

    for collection_name, contract in MART_CONTRACTS.items():
        collection = db[collection_name]
        row_count = collection.count_documents({})
        checks_run += 1
        if row_count == 0:
            errors.append(
                {
                    "collection": collection_name,
                    "check": "non_empty",
                    "message": f"{collection_name} has no rows",
                }
            )

        duplicate = next(collection.aggregate(duplicate_key_pipeline(contract["primary_key"])), None)
        checks_run += 1
        if duplicate:
            errors.append(
                {
                    "collection": collection_name,
                    "check": "unique_primary_key",
                    "message": f"{collection_name} has duplicate primary keys",
                    "details": duplicate,
                }
            )

        for field in contract["required_fields"]:
            checks_run += 1
            missing = collection.find_one({field: {"$exists": False}}, {"_id": 0})
            null_value = collection.find_one({field: None}, {"_id": 0})
            if missing or null_value:
                errors.append(
                    {
                        "collection": collection_name,
                        "check": "required_field",
                        "field": field,
                        "message": f"{collection_name}.{field} is missing or null",
                    }
                )

        for field in contract["rate_fields"]:
            checks_run += 1
            invalid_rate = collection.find_one(
                {
                    "$and": [
                        {field: {"$ne": None}},
                        {"$or": [{field: {"$lt": 0}}, {field: {"$gt": 1}}]},
                    ]
                },
                {"_id": 0},
            )
            if invalid_rate:
                errors.append(
                    {
                        "collection": collection_name,
                        "check": "rate_range",
                        "field": field,
                        "message": f"{collection_name}.{field} is outside 0..1",
                    }
                )

        geojson_field = contract.get("geojson_field")
        if geojson_field:
            checks_run += 1
            invalid_geojson = collection.find_one(
                {
                    "$or": [
                        {f"{geojson_field}.type": {"$ne": "Point"}},
                        {f"{geojson_field}.coordinates.0": {"$exists": False}},
                        {f"{geojson_field}.coordinates.1": {"$exists": False}},
                    ]
                },
                {"_id": 0},
            )
            if invalid_geojson:
                errors.append(
                    {
                        "collection": collection_name,
                        "check": "geojson_point",
                        "field": geojson_field,
                        "message": f"{collection_name}.{geojson_field} is not a valid point shape",
                    }
                )

    result = {
        "contract_checks_run": checks_run,
        "contract_failures": len(errors),
        "errors": errors,
    }
    if errors and raise_on_error:
        raise AssertionError(f"Mart contract validation failed: {errors}")
    return result


if __name__ == "__main__":
    print(validate_mart_contracts())
