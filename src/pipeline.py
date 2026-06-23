from __future__ import annotations

import argparse
import json
from datetime import datetime
from typing import Any, Callable

from src.db import get_database
from src.generate_data.generate_all import generate_all
from src.ingestion.create_indexes import create_indexes
from src.ingestion.load_raw_collections import load_raw_collections
from src.pipeline_logging import PipelineRunTracker, latest_pipeline_run, utc_now
from src.transformations.build_marts import build_all_marts
from src.transformations.contract_tests import validate_mart_contracts
from src.validation.build_clean_collections import build_clean_collections
from src.logging_config import get_logger

logger = get_logger(__name__)


StepFunction = Callable[[], dict[str, Any] | None]


def json_default(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def print_json(payload: dict[str, Any] | None) -> None:
    print(json.dumps(payload or {}, indent=2, default=json_default))


def execute_step(
    tracker: PipelineRunTracker,
    name: str,
    step_function: StepFunction,
) -> dict[str, Any]:
    logger.info(f"Starting step: {name}")
    started_at = utc_now()
    try:
        result = step_function() or {}
    except Exception as exc:
        finished_at = utc_now()
        tracker.record_step(name, "failed", started_at, finished_at, {}, str(exc))
        logger.error(f"Step {name} failed: {exc}")
        raise
    finished_at = utc_now()
    tracker.record_step(name, "success", started_at, finished_at, result)
    logger.info(f"Finished step: {name}")
    return result


def summarize_run(step_results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    generated = step_results.get("generate", {})
    loaded = step_results.get("load", {})
    validated = step_results.get("validate", {})
    transformed = step_results.get("transform", {})
    contracts = step_results.get("contracts", {})
    clean_counts = validated.get("clean_counts", {})
    mart_counts = transformed.get("mart_counts", {})
    return {
        "records_generated": generated.get("total_records", 0),
        "records_loaded": loaded.get("total_loaded_records", 0),
        "clean_records": sum(clean_counts.values()),
        "quality_issues_found": validated.get("quality_issues_found", 0),
        "quarantine_records": validated.get("quarantine_records", 0),
        "marts_built": transformed.get("marts_built", 0),
        "mart_rows": sum(mart_counts.values()),
        "contract_checks_run": contracts.get("contract_checks_run", 0),
        "contract_failures": contracts.get("contract_failures", 0),
    }


def run_all() -> dict[str, Any]:
    logger.info("Starting full pipeline run")
    tracker = PipelineRunTracker()
    run_id = tracker.start()
    step_results: dict[str, dict[str, Any]] = {}
    try:
        step_results["generate"] = execute_step(tracker, "generate", generate_all)
        step_results["load"] = execute_step(
            tracker,
            "load",
            lambda: load_raw_collections(run_id=run_id),
        )
        step_results["validate"] = execute_step(tracker, "validate", build_clean_collections)
        step_results["indexes"] = execute_step(
            tracker,
            "indexes",
            lambda: (create_indexes() or {"indexes_created": True}),
        )
        step_results["transform"] = execute_step(tracker, "transform", build_all_marts)
        step_results["contracts"] = execute_step(tracker, "contracts", validate_mart_contracts)
    except Exception as exc:
        metrics = summarize_run(step_results)
        tracker.finish("failed", metrics=metrics, error_message=str(exc))
        logger.error(f"Pipeline run failed: {exc}")
        raise

    metrics = summarize_run(step_results)
    tracker.finish("success", metrics=metrics)
    logger.info(f"Pipeline run completed successfully. Run ID: {run_id}")
    return {"run_id": run_id, "status": "success", "metrics": metrics, "steps": step_results}


def collection_status() -> dict[str, Any]:
    db = get_database()
    collections = [
        "raw_schools",
        "raw_students",
        "raw_attendance",
        "raw_assessments",
        "schools",
        "students",
        "attendance",
        "assessments",
        "quality_issues",
        "quarantine_records",
        "raw_upload_batches",
        "pipeline_runs",
        "mart_school_performance",
        "mart_regional_summary",
        "mart_term2_overview",
        "mart_data_quality",
    ]
    return {
        "latest_pipeline_run": latest_pipeline_run(),
        "collection_counts": {
            collection: db[collection].count_documents({})
            for collection in collections
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mewaka MongoDB ETL pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ["generate", "load", "validate", "indexes", "transform", "contracts", "run-all", "status"]:
        subparsers.add_parser(command)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "generate":
        print_json(generate_all())
    elif args.command == "load":
        print_json(load_raw_collections())
    elif args.command == "validate":
        print_json(build_clean_collections())
    elif args.command == "indexes":
        create_indexes()
        print_json({"indexes_created": True})
    elif args.command == "transform":
        print_json(build_all_marts())
    elif args.command == "contracts":
        print_json(validate_mart_contracts())
    elif args.command == "run-all":
        print_json(run_all())
    elif args.command == "status":
        print_json(collection_status())


if __name__ == "__main__":
    main()
