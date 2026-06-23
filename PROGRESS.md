# Project Progress And Handover

Last updated: 2026-06-23

Workspace:

```text
C:\Users\mmdip\Documents\projects\data_engineering_project
```

## Goal

Build a portfolio-grade data engineering project inspired by a dashboard data engineer job post for an education nonprofit.

The project simulates an end-to-end MongoDB data pipeline for a fictional Tanzania education program:

```text
Synthetic field data
  -> generated JSON source files
  -> raw MongoDB collections
  -> validation and quarantine
  -> clean MongoDB collections
  -> aggregation-based analytics marts
  -> Streamlit dashboard-ready outputs
```

The dashboard exists, but the current priority is the data engineering showcase: ETL pipeline design, data quality checks, observability, reproducibility, and mart contracts.

## Security Notes

- The user previously pasted a MongoDB Atlas URI in chat. Do not include or reuse that URI in files.
- Recommend rotating that Atlas password before any real use.
- The repo uses local Docker MongoDB by default.
- `.env` is ignored by Git.
- `.env.example` is safe to commit.

## Current Stack

```text
Python 3.14.3
MongoDB 7 via Docker
Mongo Express
PyMongo
Faker
Pydantic
Pandas
Streamlit
Plotly
Pytest
Docker Compose
```

## Services

Docker services are defined in:

```text
docker-compose.yml
```

Local MongoDB:

```text
mongodb://admin:adminpassword@localhost:27017/?authSource=admin
```

Mongo Express:

```text
http://localhost:8081
```

Streamlit dashboard:

```text
http://localhost:8501
```

## Important Commands

Activate venv:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start Docker services:

```powershell
docker compose up -d
```

Run full ETL pipeline:

```powershell
python -m src.pipeline run-all
```

Run individual steps:

```powershell
python -m src.pipeline generate
python -m src.pipeline load
python -m src.pipeline validate
python -m src.pipeline indexes
python -m src.pipeline transform
python -m src.pipeline contracts
python -m src.pipeline status
```

Run tests:

```powershell
python -m pytest
```

Start dashboard:

```powershell
streamlit run src/dashboard/app.py
```

Check DB connection:

```powershell
python scripts/check_connection.py
```

## Current ETL Flow

Implemented command:

```text
python -m src.pipeline run-all
```

Current pipeline steps:

```text
generate -> load -> validate -> indexes -> transform -> contracts
```

Step responsibilities:

```text
generate   Creates synthetic source JSON files.
load       Loads JSON into raw MongoDB collections and writes source metadata.
validate   Builds clean collections, logs quality issues, and writes quarantine records.
indexes    Creates uniqueness, query, and geospatial indexes.
transform  Builds dashboard-ready mart collections.
contracts  Validates mart non-emptiness, primary keys, required fields, rate ranges, and GeoJSON shape.
```

## Latest Verified Run

Latest successful run id:

```text
run_20260623_104020_42482bde
```

Latest run metrics:

```text
records_generated: 12246
records_loaded: 12246
clean_records: 12242
quality_issues_found: 80
quarantine_records: 80
marts_built: 4
mart_rows: 62
contract_checks_run: 58
contract_failures: 0
```

Latest step durations:

```text
generate: 0.975s
load: 0.834s
validate: 3.162s
indexes: 0.367s
transform: 0.745s
contracts: 0.416s
```

Test result:

```text
12 passed
```

## Latest Collection Counts

Raw/source-related:

```text
raw_schools: 36
raw_students: 1261
raw_attendance: 7776
raw_assessments: 1906
raw_upload_batches: 31
pipeline_runs: 2
```

Clean/quality:

```text
schools: 36
students: 1260
attendance: 7774
assessments: 1905
quality_issues: 80
quarantine_records: 80
```

Marts:

```text
mart_school_performance: 36
mart_regional_summary: 14
mart_term2_overview: 1
mart_data_quality: 11
```

## Synthetic Data Model

The generator now creates realistic education-program data with Tanzania-like geography.

Generated source files:

```text
schools.json
facilitators.json
data_collectors.json
field_devices.json
curriculum_modules.json
students.json
sessions.json
attendance.json
assessments.json
facilitator_visits.json
student_surveys.json
program_targets.json
source_uploads.json
interventions.json
```

Main simulation patterns:

- Schools have region, district, ward, street address, postal code, latitude, longitude, and GeoJSON `location`.
- Schools include infrastructure fields such as internet, electricity, library, projector, water access, ownership, and urban/rural context.
- Students include demographic, household, transport, phone access, risk, enrollment, dropout, and transfer fields.
- Attendance probability is affected by distance, risk, rural context, and device upload patterns.
- Sessions reference curriculum modules and facilitators.
- Assessments include total and component scores.
- Field devices and source uploads simulate late/stale/incomplete data.
- Student surveys provide satisfaction and confidence signals.
- Interventions simulate operational follow-up work.

Important: `schools.location` has a MongoDB `2dsphere` index for future map visuals.

## Raw Collections

```text
raw_schools
raw_facilitators
raw_data_collectors
raw_field_devices
raw_curriculum_modules
raw_students
raw_sessions
raw_attendance
raw_assessments
raw_facilitator_visits
raw_student_surveys
raw_program_targets
raw_source_uploads
raw_interventions
raw_upload_batches
```

## Clean Collections

```text
schools
facilitators
data_collectors
field_devices
curriculum_modules
students
sessions
attendance
assessments
facilitator_visits
student_surveys
program_targets
source_uploads
interventions
quality_issues
quarantine_records
pipeline_runs
```

## Mart Collections

```text
mart_school_performance
mart_regional_summary
mart_term2_overview
mart_data_quality
```

## Data Quality Checks

Implemented record-level and post-clean checks include:

```text
ID format checks
required field checks
accepted value checks
relationship checks
date parsing checks
score range checks
duplicate attendance checks
geospatial coordinate checks
collector/device relationship checks
source upload completeness checks
source freshness checks
field device sync freshness checks
low attendance without intervention checks
post-assessment completion checks
delivered sessions without attendance checks
facilitator caseload checks
```

Latest issue breakdown:

```text
source_contains_duplicate_records (low): 17
stale_source_data (medium): 17
source_contains_invalid_records (medium): 16
loaded_records_below_expected (medium): 15
low_post_assessment_completion (medium): 8
low_attendance_without_open_intervention (high): 2
invalid_student_relationship (high): 1
invalid_student_id (high): 1
invalid_score (high): 1
duplicate_attendance_record (medium): 1
field_device_sync_stale (medium): 1
```

## Mart Contracts

Implemented in:

```text
src/transformations/contract_tests.py
```

Contract checks verify:

```text
mart is non-empty
primary key is unique
required fields exist
required fields are not null
rate fields are between 0 and 1
school location has GeoJSON Point shape
```

Current contract result:

```text
contract_checks_run: 58
contract_failures: 0
```

## Important Files

Core pipeline:

```text
src/pipeline.py
src/pipeline_logging.py
src/run_pipeline.py
```

Data generation:

```text
src/generate_data/generate_all.py
```

Ingestion:

```text
src/ingestion/load_raw_collections.py
src/ingestion/create_indexes.py
```

Validation and quality:

```text
src/validation/build_clean_collections.py
src/validation/data_quality_checks.py
src/validation/rules.py
```

Transformations and contracts:

```text
src/transformations/build_marts.py
src/transformations/contract_tests.py
```

Dashboard:

```text
src/dashboard/app.py
```

Tests:

```text
tests/test_data_quality_checks.py
tests/test_mart_contracts.py
tests/test_pipeline_summary.py
tests/test_synthetic_generation.py
tests/test_validation_rules.py
```

Docs:

```text
docs/architecture.md
docs/data_quality_checks.md
docs/data_quality_framework.md
docs/etl_pipeline.md
docs/mart_contracts.md
docs/metric_dictionary.md
docs/operational_runbook.md
docs/synthetic_data_design.md
```

## Git State

Git was initialized, but nothing has been committed yet.

Current status shows all project files as untracked:

```text
?? .env.example
?? .gitignore
?? README.md
?? docker-compose.yml
?? docs/
?? requirements.txt
?? scripts/
?? src/
?? tests/
```

Do not commit:

```text
.env
.venv/
__pycache__/
.pytest_cache/
data/generated/*.json
screenshots/*.png
*.log
```

These are covered by `.gitignore`.

## Known Gaps

The project is functional, but these are still pending:

1. Incremental/idempotent loading is not implemented yet.
   Current raw loads use `delete_many({})` then insert source documents.

2. Clean collection building is mostly full-refresh.
   This is fine for a portfolio starter, but the next improvement should show upsert-based refresh logic.

3. Dashboard is basic compared with the data model.
   It should later include map visuals, pipeline observability, quality issue drilldowns, and an operations queue.

4. More integration tests would be useful.
   Current tests cover helpers/contracts, but not a full isolated MongoDB test run.

5. README can be made more portfolio-facing.
   It currently documents usage well, but not yet as a polished case study.

## Recommended Next Step

Next task should be:

```text
Implement idempotent/incremental loading.
```

Suggested scope:

1. Replace raw collection delete-and-insert behavior with stable upserts.
2. Define source primary keys for each raw source.
3. Add `_run_id`, `_batch_id`, `_ingested_at`, `_source_file`, and `_record_hash`.
4. Track inserted/updated/unchanged counts per source.
5. Add duplicate-source-record detection before upsert.
6. Add docs explaining idempotency and reruns.
7. Add tests for record hashing and upsert planning.

After that, do:

```text
Add dashboard pages for ETL observability and map-based school performance.
```

## Takeover Checklist

For the next model or developer:

1. Run:

```powershell
docker compose up -d
.\.venv\Scripts\Activate.ps1
python -m src.pipeline status
python -m pytest
```

2. If status is healthy, continue with incremental loading.

3. If MongoDB is empty, run:

```powershell
python -m src.pipeline run-all
```

4. Do not use the user's pasted Atlas URI. Keep local Docker as the default.

5. Preserve the project story:

```text
End-to-end MongoDB ETL pipeline for education-program dashboard metrics,
with raw/clean/mart layers, data quality checks, quarantine, observability,
contract testing, and map-ready school geography.
```

