from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.db import get_database


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def seconds_between(started_at: datetime, finished_at: datetime) -> float:
    return round((finished_at - started_at).total_seconds(), 3)


class PipelineRunTracker:
    def __init__(self, run_id: str | None = None) -> None:
        self.run_id = run_id or f"run_{utc_now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
        self.db = get_database()
        self.started_at = utc_now()

    def start(self) -> str:
        self.db.pipeline_runs.insert_one(
            {
                "run_id": self.run_id,
                "started_at": self.started_at,
                "finished_at": None,
                "duration_seconds": None,
                "status": "running",
                "steps": [],
                "metrics": {},
                "error_message": None,
            }
        )
        return self.run_id

    def record_step(
        self,
        name: str,
        status: str,
        started_at: datetime,
        finished_at: datetime,
        metrics: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        step = {
            "name": name,
            "status": status,
            "started_at": started_at,
            "finished_at": finished_at,
            "duration_seconds": seconds_between(started_at, finished_at),
            "metrics": metrics or {},
            "error_message": error_message,
        }
        self.db.pipeline_runs.update_one(
            {"run_id": self.run_id},
            {"$push": {"steps": step}},
        )

    def finish(
        self,
        status: str,
        metrics: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        finished_at = utc_now()
        self.db.pipeline_runs.update_one(
            {"run_id": self.run_id},
            {
                "$set": {
                    "finished_at": finished_at,
                    "duration_seconds": seconds_between(self.started_at, finished_at),
                    "status": status,
                    "metrics": metrics or {},
                    "error_message": error_message,
                }
            },
        )


def latest_pipeline_run() -> dict[str, Any] | None:
    db = get_database()
    return db.pipeline_runs.find_one({}, {"_id": 0}, sort=[("started_at", -1)])
