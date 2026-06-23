from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymongo import UpdateOne

from src.config import DATA_DIR
from src.db import get_database
from src.ingestion.record_hash import compute_record_hash
from src.logging_config import get_logger

logger = get_logger(__name__)


RAW_COLLECTIONS = {
    "schools.json": "raw_schools",
    "facilitators.json": "raw_facilitators",
    "data_collectors.json": "raw_data_collectors",
    "field_devices.json": "raw_field_devices",
    "curriculum_modules.json": "raw_curriculum_modules",
    "students.json": "raw_students",
    "sessions.json": "raw_sessions",
    "attendance.json": "raw_attendance",
    "assessments.json": "raw_assessments",
    "facilitator_visits.json": "raw_facilitator_visits",
    "student_surveys.json": "raw_student_surveys",
    "program_targets.json": "raw_program_targets",
    "source_uploads.json": "raw_source_uploads",
    "interventions.json": "raw_interventions",
}

RAW_PRIMARY_KEYS = {
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


def read_json(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_raw_collections(run_id: str | None = None) -> dict[str, Any]:
    db = get_database()
    batch_id = f"batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"
    ingested_at = datetime.now(timezone.utc)

    load_stats: dict[str, Any] = {
        "batch_id": batch_id,
        "sources": {},
        "total_loaded_records": 0,
        "total_inserted": 0,
        "total_updated": 0,
        "total_unchanged": 0,
    }

    for filename, collection_name in RAW_COLLECTIONS.items():
        path = DATA_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing generated file: {path}")

        rows = read_json(path)
        collection = db[collection_name]
        pk_field = RAW_PRIMARY_KEYS[collection_name]

        existing_records = {
            doc.get(pk_field): doc.get("_record_hash")
            for doc in collection.find({}, {pk_field: 1, "_record_hash": 1})
            if pk_field in doc
        }

        operations = []
        stats = {"inserted": 0, "updated": 0, "unchanged": 0}

        for row in rows:
            record_hash = compute_record_hash(row)
            pk_val = row.get(pk_field)

            if pk_val in existing_records:
                if existing_records[pk_val] == record_hash:
                    stats["unchanged"] += 1
                    continue
                else:
                    stats["updated"] += 1
                    doc = {
                        **row,
                        "_batch_id": batch_id,
                        "_source_file": filename,
                        "_record_hash": record_hash,
                        "_run_id": run_id,
                        "_updated_at": ingested_at,
                    }
                    operations.append(UpdateOne({pk_field: pk_val}, {"$set": doc}))
            else:
                stats["inserted"] += 1
                doc = {
                    **row,
                    "_batch_id": batch_id,
                    "_source_file": filename,
                    "_record_hash": record_hash,
                    "_run_id": run_id,
                    "_ingested_at": ingested_at,
                    "_updated_at": ingested_at,
                }
                operations.append(UpdateOne({pk_field: pk_val}, {"$set": doc}, upsert=True))

        if operations:
            collection.bulk_write(operations)

        source_name = collection_name.replace("raw_", "")
        db.raw_upload_batches.insert_one(
            {
                "batch_id": batch_id,
                "run_id": run_id,
                "source_name": source_name,
                "source_file": filename,
                "raw_collection": collection_name,
                "source_path": str(path),
                "expected_records": len(rows),
                "loaded_records": len(rows),
                "inserted_records": stats["inserted"],
                "updated_records": stats["updated"],
                "unchanged_records": stats["unchanged"],
                "invalid_records": 0,
                "duplicate_records": 0,
                "ingested_at": ingested_at,
                "pipeline_status": "Loaded",
            }
        )
        load_stats["sources"][collection_name] = stats
        load_stats["total_loaded_records"] += len(rows)
        load_stats["total_inserted"] += stats["inserted"]
        load_stats["total_updated"] += stats["updated"]
        load_stats["total_unchanged"] += stats["unchanged"]
        
        logger.info(
            f"Loaded {collection_name}: {stats['inserted']} inserted, "
            f"{stats['updated']} updated, {stats['unchanged']} unchanged"
        )

    return load_stats


if __name__ == "__main__":
    load_raw_collections()
