# 🌍 Mewaka Program Metrics - End-to-End Education Data Pipeline

<a href="https://tanzania-education-pipeline-vmpnvhngvqdisvuz3kcc9d.streamlit.app/" target="_blank"><img src="https://img.shields.io/badge/View_Live_Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="View Live Dashboard"/></a>

> **Status:** Live | Pipeline Passing | 0 Contract Failures

A production-grade data engineering pipeline built for a fictional education program in Tanzania. This project simulates the full operational data stack of an NGO - from raw field data collection through to a live analytics dashboard - showcasing MongoDB data architecture, idempotent ETL design, modular validation, and real-time observability.

## 📌 Project Description

This is a complete, end-to-end data engineering portfolio project built around a realistic problem: **how does a social impact organization track whether its education program is actually working — and how does it trust the data behind that question?**

I designed and built a Python + MongoDB ETL pipeline that ingests synthetic field data (schools, students, attendance, assessments, facilitator visits), validates and cleans it through a modular quality layer, builds analytics-ready mart tables, and surfaces everything through an interactive Streamlit dashboard.

The pipeline processes **12,246 records across 14 entity types**, runs **58 contract checks** on every execution, and catches and quarantines data quality issues automatically — with zero failures in the latest run.

## 1. The Problem

Education NGOs operating at scale face a data trust problem. Field staff collect attendance and assessment records on mobile devices across dozens of rural schools. Those records get uploaded in batches — sometimes late, sometimes incomplete, sometimes with broken device IDs or missing school references. By the time the data reaches a dashboard, nobody knows:

- Which records were already loaded vs. genuinely new
- Whether a student's assessment score is real or a sync artifact
- Which schools are generating unreliable data vs. genuine underperformance
- Whether the pipeline ran cleanly this week or silently dropped records

The result: program managers make decisions on data they can't fully trust.

## 2. The Solution I Built

I built a layered ETL pipeline that treats data quality as a first-class concern at every stage - not an afterthought.

```mermaid
flowchart TD
    subgraph Source
        A[Synthetic Field Data]
    end
    
    subgraph Ingestion
        B[(Raw MongoDB Collections)]
    end
    
    subgraph Quality
        C{Modular Validator Engine}
        D[Quarantine Collections]
    end
    
    subgraph Analytics
        E[(Clean Collections)]
        F[(Mart Collections)]
    end
    
    subgraph Serving
        G[Streamlit Dashboard]
        H[Contract Tests]
    end

    A -->|Idempotent Upsert| B
    B -->|Validation Rules| C
    C -->|Invalid| D
    C -->|Valid| E
    E -->|Aggregations| F
    F --> G
    F --> H
```

Every pipeline run is fully **idempotent**: re-running it on the same data detects unchanged records and skips them, updates modified ones, and only inserts genuinely new records. The dashboard includes a **Pipeline Monitor** page that exposes exactly what happened in each run - records inserted vs. updated vs. unchanged, step durations, quality issues caught, and contract results.

## 3. Technical Architecture

### 3.1 Data Model

The pipeline manages **14 raw source entities** and promotes them through three database layers:

| Layer | Collections | Purpose |
|-------|-------------|---------|
| **Raw** | `raw_schools`, `raw_students`, `raw_attendance`, `raw_assessments`, + 10 more | Source-of-truth ingestion with full lineage metadata |
| **Clean** | `schools`, `students`, `attendance`, `assessments`, + quality/quarantine tables | Validated, referentially-complete records |
| **Mart** | `mart_school_performance`, `mart_regional_summary`, `mart_term2_overview`, `mart_data_quality` | Aggregated, dashboard-ready outputs |

### 3.2 Idempotent Loading

Raw collection loading uses **SHA-256 record hashing** to fingerprint each incoming record (excluding metadata fields). On re-run:

- Records whose hash matches the stored hash → **skipped** (unchanged)
- Records whose hash changed → **updated** via `pymongo.UpdateOne` upsert
- Net-new records → **inserted**

This makes every pipeline run safe to re-execute without data duplication, and produces change statistics per batch visible in the dashboard.

### 3.3 Modular Validation Layer

Rather than a single monolithic validation script, I built a **`src/validation/validators/`** package with separate validator modules per entity domain:

```text
validators/
  schools.py       - ID format, required fields, geolocation bounds (Tanzania lat/lon)
  students.py      - School FK check, enrollment date, dropout logic, gender normalization
  sessions.py      - Module/facilitator FK checks, date ordering
  attendance.py    - Student/session FK checks, duplicate (student, session) detection
  assessments.py   - Score range validation, assessment type constraints
  facilitators.py  - ID format, contract field extraction
  common.py        - Collectors, devices, modules, visits, surveys, targets, uploads
```

A shared `ValidatorContext` dataclass carries resolved entity ID sets across validators so that downstream entities (e.g. attendance) can reference upstream validated sets (e.g. `student_ids`) without re-querying MongoDB.

Invalid records are **quarantined** with their full raw payload, issue type, severity, and batch context - not silently dropped.

### 3.4 Data Quality Checks

The validation layer runs **16 categories of checks** across all entity types:

| Check Type | Example |
|-----------|---------|
| ID format | `school_id` must match expected pattern |
| Required fields | `school_name`, `region`, `district` must be present |
| FK integrity | Student's `school_id` must exist in validated schools |
| Geolocation bounds | Tanzania latitude: -12° to 0°, longitude: 28° to 42° |
| Date ordering | `dropout_date` must not precede `enrollment_date` |
| Score range | Assessment scores must be between 0 and 100 |
| Duplicate detection | Same `(student_id, session_id)` pair cannot appear twice |
| Source freshness | Source uploads older than 30 days are flagged |
| Device sync staleness | Field devices not synced in 14 days are flagged |
| Intervention coverage | Schools with low attendance and no open intervention are flagged |

**Latest Run Results:**
```text
Quality issues caught:    80
Quarantined records:      80
Contract checks passed:   58 / 58
Contract failures:        0
```

### 3.5 Pipeline Observability

Every run writes a structured run document to `pipeline_runs` containing:

- Unique `run_id` with timestamp
- Per-step status, duration, and metrics
- Batch-level change statistics (inserted / updated / unchanged per collection)
- Contract check results

This is surfaced directly in the **Pipeline Monitor** dashboard page.

### 3.6 Mart Contract Tests

Before the pipeline marks itself as successful, it runs **58 automated contract checks** across all mart collections verifying:

- Mart is non-empty
- Primary keys are unique
- Required fields are present and non-null
- Rate fields fall within `[0, 1]`
- GeoJSON `location` fields conform to the correct Point schema

## 4. Dashboard

The Streamlit dashboard provides six analytical views:

| Page | Description |
|------|-------------|
| **Executive Overview** | Topline metrics: schools, active students, attendance rate, session delivery, at-risk count |
| **Term 2 Performance** | District-level bar charts with selectable KPI metrics |
| **School Map** | Interactive Plotly Mapbox scatter, colored by risk status, sized by enrollment |
| **School Drilldown** | Per-school full profile with all performance metrics |
| **Assessment Outcomes** | Score distributions by gender and assessment type |
| **Data Quality Monitor** | Issue breakdown by collection, severity, and type |
| **Pipeline Monitor** | Latest run metadata, step durations, batch change statistics |

## 5. Synthetic Data Design

The data generator produces realistic field-program data - not toy examples. Key simulation patterns include:

- **Tanzania geography**: 36 schools across 9 regions with real district names, street addresses, and bounding-box-validated coordinates
- **Infrastructure modeling**: Schools have electricity, internet, projector, library, and water access fields that correlate with performance outcomes
- **Behavioral simulation**: Rural schools have higher upload delays, higher absence rates, and more late submissions
- **Student lifecycle**: Enrollment, dropout, transfer, and active status with realistic date sequencing
- **Assessment structure**: Total score plus sub-scores for business skills, financial literacy, communication, and problem solving
- **Intervention tracking**: Low-attendance flags trigger simulated intervention records with priority, due date, and outcome

## 6. Stack

| Layer | Technology |
|-------|-----------|
| Database | MongoDB 7 (Docker) + Mongo Express |
| ETL | Python 3.14, PyMongo |
| Data Generation | Faker |
| Validation | Custom rule engine (no external framework) |
| Dashboard | Streamlit + Plotly |
| Testing | Pytest (16 tests) |
| Infrastructure | Docker Compose |
| Dependency pinning | `requirements-lock.txt` |

## 7. How to Run

**Start MongoDB:**
```powershell
docker compose up -d
```

**Create and activate virtual environment:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**Run the full pipeline:**
```powershell
python -m src.pipeline run-all
```

**Check pipeline status:**
```powershell
python -m src.pipeline status
```

**Run tests:**
```powershell
python -m pytest
```

**Launch dashboard:**
```powershell
streamlit run src/dashboard/app.py
```

**Mongo Express UI:** [http://localhost:8081](http://localhost:8081)

## 8. Running Individual Pipeline Steps

```powershell
python -m src.pipeline generate    # Generate synthetic source JSON files
python -m src.pipeline load        # Ingest into raw MongoDB collections
python -m src.pipeline validate    # Validate, clean, and quarantine
python -m src.pipeline indexes     # Create MongoDB indexes
python -m src.pipeline transform   # Build mart collections
python -m src.pipeline contracts   # Run automated contract checks
```

## 9. Latest Verified Run

```text
Run ID:                run_20260623_130707_475be7d8
Status:                success

Records generated:     12,246
Records loaded:        12,246
Clean records:         12,242
Quality issues found:  80
Quarantine records:    80
Marts built:           4
Contract checks run:   58
Contract failures:     0
```

Step durations:
```text
generate:   ~1.0s
load:       ~28.0s  (SHA-256 hash comparison across 12k records)
validate:   ~4.0s
indexes:    ~0.4s
transform:  ~0.7s
contracts:  ~0.4s
```

## 10. Configuration

Copy `.env.example` to `.env` and adjust as needed:

```env
MONGO_URI=mongodb://admin:adminpassword@localhost:27017/?authSource=admin
MONGO_DB=mewaka_program_metrics
```

To use MongoDB Atlas, replace `MONGO_URI` with your Atlas connection string. **Do not commit real credentials.**

## 11. Project Structure

```text
src/
  pipeline.py                     Pipeline orchestrator
  logging_config.py               Centralized logging setup
  db.py                           MongoDB connection management
  config.py                       Environment configuration
  generate_data/
    generate_all.py               Synthetic data generator
  ingestion/
    load_raw_collections.py       Idempotent upsert loader
    record_hash.py                SHA-256 record fingerprinting
    create_indexes.py             MongoDB index creation
  validation/
    build_clean_collections.py    Validation orchestrator
    data_quality_checks.py        Post-clean quality checks
    rules.py                      Field-level validation rules
    validators/
      __init__.py                 ValidatorContext dataclass
      schools.py
      students.py
      sessions.py
      attendance.py
      assessments.py
      facilitators.py
      common.py
  transformations/
    build_marts.py                Mart aggregation logic
    contract_tests.py             Automated contract checks
  dashboard/
    app.py                        Streamlit dashboard
docs/
  architecture.md
  etl_pipeline.md
  idempotent_loading.md
  data_quality_checks.md
  mart_contracts.md
  operational_runbook.md
tests/
  test_record_hash.py
  test_idempotent_loading.py
  test_data_quality_checks.py
  test_mart_contracts.py
  test_pipeline_summary.py
  test_synthetic_generation.py
  test_validation_rules.py
```

*Data note: This project uses entirely synthetic data generated with Faker and custom simulation logic. No real student or school records are used. The program, school names, and geography are fictional.*
