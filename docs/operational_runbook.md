# Operational Runbook

## Start Services

```powershell
docker compose up -d
```

## Run The ETL Pipeline

```powershell
.\.venv\Scripts\Activate.ps1
python -m src.pipeline run-all
```

## Check Pipeline Status

```powershell
python -m src.pipeline status
```

## Run Mart Contract Checks

```powershell
python -m src.pipeline contracts
```

## Run Tests

```powershell
python -m pytest
```

## Inspect MongoDB

Mongo Express:

```text
http://localhost:8081
```

Local MongoDB URI:

```text
mongodb://admin:adminpassword@localhost:27017/?authSource=admin
```

## Troubleshooting

If MongoDB connection fails:

```powershell
docker ps --filter "name=mewaka"
python scripts/check_connection.py
```

If the pipeline fails:

```powershell
python -m src.pipeline status
```

Then inspect the latest `pipeline_runs` document and the `quarantine_records` collection.
