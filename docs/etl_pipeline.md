# ETL Pipeline

This project is organized as an end-to-end data engineering pipeline.

```text
Synthetic field sources
  -> generated JSON files
  -> raw MongoDB collections
  -> validation and quarantine
  -> clean MongoDB collections
  -> aggregation transformations
  -> dashboard mart collections
```

## Commands

Run the full pipeline:

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

## Pipeline Steps

| Step | Purpose | Main Outputs |
| --- | --- | --- |
| `generate` | Builds realistic synthetic source files. | `data/generated/*.json` |
| `load` | Loads generated files into raw MongoDB collections with ingestion metadata. | `raw_*`, `raw_upload_batches` |
| `validate` | Standardizes data, checks relationships, logs quality issues, quarantines bad records. | clean collections, `quality_issues`, `quarantine_records` |
| `indexes` | Creates query, uniqueness, and geospatial indexes. | MongoDB indexes |
| `transform` | Builds dashboard-ready analytics collections with aggregation pipelines. | `mart_*` |
| `contracts` | Verifies mart uniqueness, required fields, rate ranges, and GeoJSON shape. | contract check metrics |

## Observability

Every `run-all` execution writes to `pipeline_runs`.

Each run includes:

- Run id
- Started and finished timestamps
- Status
- Step-level durations
- Step-level metrics
- Final summary metrics
- Error message if failed

The final run summary includes generated, loaded, cleaned, quarantined, transformed, and contract-check metrics.

The ingestion step writes one `raw_upload_batches` document per source file, including expected records, loaded records, raw collection, source file, batch id, and run id.
