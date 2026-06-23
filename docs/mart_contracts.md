# Mart Contracts

## `mart_school_performance`

Grain: one row per school per term.

Primary key:

```text
school_id
```

Sources:

```text
schools
students
sessions
attendance
assessments
facilitator_visits
student_surveys
interventions
quality_issues
```

Selected metrics:

- Active students
- High-risk students
- Attendance rate
- Late submission rate
- Session delivery rate
- Assessment completion rate
- Facilitator visit completion rate
- Average delivery quality score
- Average satisfaction score
- Average distance to school
- Open interventions
- Data quality issues
- Risk status

Contract checks:

- Non-empty
- Unique `school_id`
- Required geography and KPI fields
- Rate fields between 0 and 1
- GeoJSON point shape for `location`

## `mart_regional_summary`

Grain: one row per region and district.

Primary key:

```text
region, district
```

Sources:

```text
mart_school_performance
```

Selected metrics:

- School count
- Active students
- High-risk students
- Average attendance rate
- Average session delivery rate
- Average assessment completion rate
- Average late submission rate
- Average satisfaction score
- Open interventions
- At-risk schools

Contract checks:

- Non-empty
- Unique `region, district`
- Required district KPI fields
- Rate fields between 0 and 1

## `mart_term2_overview`

Grain: one row for Term 2.

Primary key:

```text
term
```

Sources:

```text
mart_school_performance
```

Selected metrics:

- Total schools
- Active students
- High-risk students
- Average attendance rate
- Average session delivery rate
- Average assessment completion rate
- Average visit completion rate
- Average late submission rate
- Open interventions
- Data quality issues

Contract checks:

- Non-empty
- Unique `term`
- Required executive KPI fields
- Rate fields between 0 and 1

## `mart_data_quality`

Grain: one row per source collection, issue type, and severity.

Primary key:

```text
collection, issue_type, severity
```

Sources:

```text
quality_issues
```

Selected metrics:

- Issue count

Contract checks:

- Non-empty
- Unique `collection, issue_type, severity`
- Required quality issue fields
