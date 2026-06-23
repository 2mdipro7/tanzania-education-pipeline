# Synthetic Data Design

The generated database simulates a Tanzania education program with the kinds of operational patterns dashboard teams usually need to monitor.

## Geography

Schools are distributed across five regions:

- Arusha
- Dar es Salaam
- Dodoma
- Mwanza
- Mbeya

Each school has:

- Region and district
- Ward
- Street address
- Postal code
- Latitude and longitude
- GeoJSON `location` point
- Urban/rural classification

The `schools.location` field is indexed as `2dsphere`, so future dashboard work can add map views and proximity analysis.

## Program Operations

The simulation includes:

- Facilitators and assigned school caseloads
- Data collectors
- Field devices with connectivity quality
- Curriculum modules
- Planned and delivered sessions
- Attendance records
- Pre/post assessments
- Student surveys
- Source uploads
- Interventions

## Realistic Trends

The generator uses simple but useful program assumptions:

- Rural districts tend to have weaker connectivity and longer travel distance.
- Longer travel distance reduces attendance probability.
- Students with less phone access and lower baseline confidence are more likely to become high risk.
- Schools with stronger infrastructure have better session delivery.
- Poor field-device connectivity creates late submissions.
- High-risk students are more likely to trigger follow-up interventions.
- Student assessment gains are correlated with baseline score, attendance context, and phone access.

## Intentional Data Quality Issues

The generated raw layer includes a small number of deliberate issues:

- Invalid student relationship
- Duplicate attendance record
- Missing student ID in attendance
- Invalid assessment score

These are expected and should appear in `quality_issues` and `mart_data_quality`.
