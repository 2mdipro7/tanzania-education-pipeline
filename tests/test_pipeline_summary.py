from src.pipeline import summarize_run


def test_summarize_run_collects_core_etl_metrics() -> None:
    summary = summarize_run(
        {
            "generate": {"total_records": 10},
            "load": {"total_loaded_records": 9},
            "validate": {
                "clean_counts": {"students": 7, "schools": 2},
                "quality_issues_found": 1,
                "quarantine_records": 1,
            },
            "transform": {
                "mart_counts": {"mart_school_performance": 2, "mart_data_quality": 1},
                "marts_built": 2,
            },
        }
    )

    assert summary["records_generated"] == 10
    assert summary["records_loaded"] == 9
    assert summary["clean_records"] == 9
    assert summary["quality_issues_found"] == 1
    assert summary["quarantine_records"] == 1
    assert summary["marts_built"] == 2
    assert summary["mart_rows"] == 3
    assert summary["contract_checks_run"] == 0
    assert summary["contract_failures"] == 0
