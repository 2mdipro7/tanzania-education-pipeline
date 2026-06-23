# Handover Checklist

Use `PROGRESS.md` as the full takeover brief. This file is the short checklist.

## Resume Commands

```powershell
docker compose up -d
.\.venv\Scripts\Activate.ps1
python -m src.pipeline status
python -m pytest
```

## Current Healthy State

Latest verified pipeline:

```text
run_20260623_104020_42482bde
```

Expected result:

```text
status: success
quality_issues_found: 80
quarantine_records: 80
contract_checks_run: 58
contract_failures: 0
tests: 12 passed
```

## Continue Here

Next recommended task:

```text
Implement idempotent/incremental loading.
```

Target changes:

- Add stable source primary keys.
- Add record hashing.
- Replace raw full refresh with upserts.
- Track inserted, updated, unchanged, duplicate counts.
- Document rerun behavior.
- Add tests for hash/upsert logic.

## Do Not Do

- Do not commit `.env`.
- Do not use or repeat the user's pasted MongoDB Atlas URI.
- Do not remove existing ETL observability or quality checks.
- Do not turn the project into only a dashboard demo; the primary story is data engineering.

