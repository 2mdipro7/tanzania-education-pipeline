# Architecture

```text
data generator
  -> generated JSON files
  -> raw MongoDB collections
  -> validation and cleaning
  -> clean MongoDB collections
  -> aggregation pipelines
  -> dashboard mart collections
  -> Streamlit dashboard
```

The project keeps raw and clean data separate. Raw records receive batch metadata for traceability, while invalid records are logged to `quality_issues` instead of being silently dropped.

The clean `schools` collection stores both address fields and a GeoJSON `location` field. The index layer creates a `2dsphere` index so map-based dashboard work can query the same curated data used by the marts.
