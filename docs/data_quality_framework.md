# Data Quality Framework

The validation layer checks:

- Required fields
- ID format
- Valid categorical values
- Valid score ranges
- Student-school relationships
- Session-school relationships
- Attendance duplicates
- Missing assessment records
- Late or incomplete program activity records

Each issue is written to `quality_issues` with collection, record id, severity, issue type, field, batch id, and detection timestamp.

