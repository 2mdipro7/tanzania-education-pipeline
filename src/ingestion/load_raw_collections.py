from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import DATA_DIR
from src.db import get_database


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
    }

    for filename, collection_name in RAW_COLLECTIONS.items():
        path = DATA_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing generated file: {path}")

        rows = read_json(path)
        documents = [
            {
                **row,
                "_batch_id": batch_id,
                "_source_file": filename,
                "_ingested_at": ingested_at,
            }
            for row in rows
        ]
        collection = db[collection_name]
        collection.delete_many({})
        if documents:
            collection.insert_many(documents)
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
                "loaded_records": len(documents),
                "invalid_records": 0,
                "duplicate_records": 0,
                "ingested_at": ingested_at,
                "pipeline_status": "Loaded",
            }
        )
        load_stats["sources"][collection_name] = len(documents)
        load_stats["total_loaded_records"] += len(documents)
        print(f"Loaded {len(documents)} documents into {collection_name}")
    return load_stats


if __name__ == "__main__":
    load_raw_collections()
