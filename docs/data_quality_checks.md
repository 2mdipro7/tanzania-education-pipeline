# Data Quality Checks

The validation layer is designed to resemble dbt-style checks implemented for MongoDB collections.

## Current Checks

| Category | Examples |
| --- | --- |
| ID format | Student IDs must match `STU_00001`, attendance IDs must match `ATT_000001`, etc. |
| Required fields | Schools require school id, name, region, and district. |
| Accepted values | Gender, status, assessment type, and visit status are standardized. |
| Relationship checks | Students must map to valid schools; attendance must map to valid students and sessions. |
| Date checks | Enrollment, planned, delivered, assessment, survey, and upload dates are parsed and standardized. |
| Range checks | Assessment scores must be between 0 and 100. |
| Duplicate checks | Student-session attendance records must be unique. |
| Geospatial checks | School latitude and longitude must be valid Tanzania-like coordinates. |
| Device/collector checks | Attendance records must reference known collectors and devices. |
| Source completeness | Source uploads are checked for loaded records below expected counts. |
| Freshness | Source uploads and field devices are checked for stale record dates or sync dates. |
| Operational gaps | Low attendance without an open intervention is flagged. |
| Assessment completeness | Schools with low post-assessment completion are flagged. |
| Session completeness | Delivered sessions without attendance records are flagged. |
| Workload checks | Facilitator caseload above threshold is flagged. |

## Quality Outputs

`quality_issues` stores a compact issue log:

```text
collection
record_id
issue_type
severity
field
batch_id
school_id
detected_at
```

`quarantine_records` stores the rejected raw document:

```text
source_collection
record_id
issue_type
severity
field
batch_id
school_id
detected_at
raw_record
```

This makes the pipeline auditable without hiding bad source records.

## Contract Checks

After mart builds, the pipeline runs contract checks against dashboard-ready collections:

- Mart is non-empty
- Primary key is unique
- Required fields exist and are not null
- Rate metrics stay between 0 and 1
- School mart location fields have GeoJSON point shape
