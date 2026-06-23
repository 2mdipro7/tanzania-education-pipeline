# Tanzania Education Program Metrics Pipeline

MongoDB-based data engineering portfolio project that simulates dashboard infrastructure for an education program in Tanzania.

The project generates synthetic field data, loads it into raw MongoDB collections, validates and cleans records, builds indexed trusted collections, creates dashboard-ready mart collections, and exposes metrics through a Streamlit dashboard.

The synthetic data now includes realistic program operations signals: Tanzania region/district geography, school addresses and GeoJSON coordinates, school infrastructure, facilitators, field devices, source uploads, student demographics, attendance patterns, assessments, surveys, and intervention follow-ups.

## Stack

- MongoDB local container
- Mongo Express admin UI
- Python
- PyMongo
- Pydantic
- Faker
- Streamlit
- Plotly
- Pytest

## Quick Start

Start MongoDB:

```powershell
docker compose up -d
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Check MongoDB:

```powershell
python scripts/check_connection.py
```

Run the pipeline:

```powershell
python -m src.pipeline run-all
```

Check pipeline status:

```powershell
python -m src.pipeline status
```

Start the dashboard:

```powershell
streamlit run src/dashboard/app.py
```

Mongo Express is available at:

```text
http://localhost:8081
```

## Pipeline

```text
Synthetic field data
-> raw MongoDB collections
-> validation and quality issue logging
-> clean trusted collections
-> dashboard-ready mart collections
-> Streamlit dashboard
```

## Database

Default database:

```text
mewaka_program_metrics
```

Raw collections:

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

Clean collections:

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
```

Mart collections:

```text
mart_school_performance
mart_regional_summary
mart_term2_overview
mart_data_quality
```

Pipeline observability collections:

```text
pipeline_runs
raw_upload_batches
quarantine_records
```

## ETL Showcase

This project includes an observable ETL pipeline:

```text
generate -> load -> validate -> indexes -> transform -> contracts
```

The full run writes step-level metrics to `pipeline_runs`. Source-file metadata is written to `raw_upload_batches`, invalid raw records are retained in `quarantine_records`, and mart contract checks verify that dashboard outputs are non-empty, uniquely keyed, complete, and within expected ranges.

See:

- `docs/etl_pipeline.md`
- `docs/data_quality_checks.md`
- `docs/mart_contracts.md`
- `docs/operational_runbook.md`

## Synthetic Data Design

The generator intentionally models realistic operational trends:

- Rural schools are more likely to have limited internet, longer student travel distances, and weaker upload timeliness.
- Student attendance is affected by distance to school, baseline risk, phone access, and school context.
- Session delivery is affected by school infrastructure, implementation status, and contextual risk.
- Field device connectivity affects upload delay and late submissions.
- Assessments include component scores for business, financial literacy, communication, and problem solving.
- Surveys add satisfaction and confidence signals for monitoring and evaluation.
- Interventions track follow-up work for low attendance, delivery support, missing assessments, and data correction requests.
- Schools include `latitude`, `longitude`, and GeoJSON `location` fields for future map-based visuals.

## Atlas

This project defaults to local Docker MongoDB. To use MongoDB Atlas, replace `MONGO_URI` in `.env` with your Atlas connection string.

Do not commit real credentials.
