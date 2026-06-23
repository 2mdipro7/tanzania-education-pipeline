from __future__ import annotations

from pymongo import ASCENDING, GEOSPHERE

from src.db import get_database
from src.logging_config import get_logger

logger = get_logger(__name__)


def create_indexes() -> None:
    db = get_database()

    for mart_collection in [
        "mart_regional_summary",
        "mart_term2_overview",
        "mart_data_quality",
    ]:
        db[mart_collection].drop_indexes()

    db.schools.create_index([("school_id", ASCENDING)], unique=True)
    db.schools.create_index([("region", ASCENDING), ("district", ASCENDING)])
    db.schools.create_index([("location", GEOSPHERE)])
    db.schools.create_index([("urban_rural", ASCENDING), ("implementation_status", ASCENDING)])

    db.facilitators.create_index([("facilitator_id", ASCENDING)], unique=True)
    db.facilitators.create_index([("region", ASCENDING), ("primary_district", ASCENDING)])

    db.data_collectors.create_index([("collector_id", ASCENDING)], unique=True)
    db.data_collectors.create_index([("assigned_region", ASCENDING), ("assigned_district", ASCENDING)])

    db.field_devices.create_index([("device_id", ASCENDING)], unique=True)
    db.field_devices.create_index([("connectivity_quality", ASCENDING)])

    db.curriculum_modules.create_index([("module_id", ASCENDING)], unique=True)
    db.curriculum_modules.create_index([("term", ASCENDING), ("week_number", ASCENDING)])

    db.students.create_index([("student_id", ASCENDING)], unique=True)
    db.students.create_index([("school_id", ASCENDING)])
    db.students.create_index([("status", ASCENDING)])
    db.students.create_index([("baseline_risk_level", ASCENDING)])

    db.sessions.create_index([("session_id", ASCENDING)], unique=True)
    db.sessions.create_index([("school_id", ASCENDING), ("term", ASCENDING)])
    db.sessions.create_index([("module_id", ASCENDING), ("delivery_status", ASCENDING)])

    db.attendance.create_index([("student_id", ASCENDING), ("session_id", ASCENDING)], unique=True)
    db.attendance.create_index([("session_id", ASCENDING)])
    db.attendance.create_index([("school_id", ASCENDING), ("attendance_date", ASCENDING)])
    db.attendance.create_index([("is_late_submission", ASCENDING)])

    db.assessments.create_index([("student_id", ASCENDING), ("assessment_type", ASCENDING)])
    db.assessments.create_index([("term", ASCENDING)])
    db.assessments.create_index([("school_id", ASCENDING), ("assessment_type", ASCENDING)])

    db.facilitator_visits.create_index([("school_id", ASCENDING), ("planned_date", ASCENDING)])
    db.facilitator_visits.create_index([("facilitator_id", ASCENDING), ("visit_status", ASCENDING)])
    db.student_surveys.create_index([("school_id", ASCENDING), ("term", ASCENDING)])
    db.source_uploads.create_index([("source_name", ASCENDING), ("uploaded_at", ASCENDING)])
    db.interventions.create_index([("school_id", ASCENDING), ("status", ASCENDING)])
    db.interventions.create_index([("assigned_to", ASCENDING), ("priority", ASCENDING)])
    db.quality_issues.create_index([("collection", ASCENDING), ("issue_type", ASCENDING)])
    db.quarantine_records.create_index([("source_collection", ASCENDING), ("issue_type", ASCENDING)])
    db.quarantine_records.create_index([("batch_id", ASCENDING)])
    db.raw_upload_batches.create_index([("batch_id", ASCENDING), ("source_name", ASCENDING)])
    db.raw_upload_batches.create_index([("run_id", ASCENDING)])
    db.pipeline_runs.create_index([("run_id", ASCENDING)], unique=True)
    db.pipeline_runs.create_index([("started_at", ASCENDING), ("status", ASCENDING)])

    db.mart_school_performance.create_index([("school_id", ASCENDING)], unique=True)
    db.mart_regional_summary.create_index(
        [("region", ASCENDING), ("district", ASCENDING)],
        unique=True,
    )
    db.mart_term2_overview.create_index([("term", ASCENDING)], unique=True)
    db.mart_data_quality.create_index(
        [
            ("collection", ASCENDING),
            ("issue_type", ASCENDING),
            ("severity", ASCENDING),
        ],
        unique=True,
    )
    logger.info("Indexes created")


if __name__ == "__main__":
    create_indexes()
