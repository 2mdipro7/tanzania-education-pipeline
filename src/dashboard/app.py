from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db import get_database


st.set_page_config(page_title="Mewaka Program Metrics", layout="wide")


@st.cache_data(ttl=60)
def load_collection(name: str) -> pd.DataFrame:
    db = get_database()
    rows = list(db[name].find({}, {"_id": 0}))
    return pd.DataFrame(rows)


def pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.1f}%"


st.title("Tanzania Education Program Metrics")

page = st.sidebar.radio(
    "View",
    [
        "Executive Overview",
        "Term 2 Performance",
        "School Drilldown",
        "Assessment Outcomes",
        "Data Quality Monitor",
    ],
)

school_df = load_collection("mart_school_performance")
regional_df = load_collection("mart_regional_summary")
overview_df = load_collection("mart_term2_overview")
quality_df = load_collection("mart_data_quality")

if page == "Executive Overview":
    if overview_df.empty:
        st.warning("Run `python -m src.run_pipeline` to build dashboard marts.")
        st.stop()

    overview = overview_df.iloc[0]
    cols = st.columns(6)
    cols[0].metric("Schools", int(overview["schools"]))
    cols[1].metric("Active Students", int(overview["active_students"]))
    cols[2].metric("Attendance", pct(overview["avg_attendance_rate"]))
    cols[3].metric("Session Delivery", pct(overview["avg_session_delivery_rate"]))
    cols[4].metric("Assessments", pct(overview["avg_assessment_completion_rate"]))
    cols[5].metric("At-Risk Schools", int(overview["at_risk_schools"]))

    left, right = st.columns(2)
    with left:
        st.subheader("School Risk")
        risk_counts = school_df["risk_status"].value_counts().reset_index()
        risk_counts.columns = ["risk_status", "schools"]
        st.plotly_chart(
            px.bar(risk_counts, x="risk_status", y="schools", color="risk_status"),
            use_container_width=True,
        )
    with right:
        st.subheader("District Attendance")
        st.plotly_chart(
            px.bar(
                regional_df.sort_values("avg_attendance_rate"),
                x="avg_attendance_rate",
                y="district",
                color="region",
                orientation="h",
            ),
            use_container_width=True,
        )

elif page == "Term 2 Performance":
    st.subheader("District Performance")
    metric = st.selectbox(
        "Metric",
        [
            "avg_attendance_rate",
            "avg_session_delivery_rate",
            "avg_assessment_completion_rate",
        ],
    )
    st.plotly_chart(
        px.bar(
            regional_df.sort_values(metric, ascending=False),
            x="district",
            y=metric,
            color="region",
            hover_data=["schools", "active_students", "at_risk_schools"],
        ),
        use_container_width=True,
    )
    st.dataframe(regional_df, use_container_width=True)

elif page == "School Drilldown":
    if school_df.empty:
        st.warning("No school mart data found.")
        st.stop()
    school_name = st.selectbox("School", school_df["school_name"].sort_values())
    school = school_df[school_df["school_name"] == school_name].iloc[0]
    cols = st.columns(5)
    cols[0].metric("Active Students", int(school["active_students"]))
    cols[1].metric("Attendance", pct(school["attendance_rate"]))
    cols[2].metric("Session Delivery", pct(school["session_delivery_rate"]))
    cols[3].metric("Assessment Completion", pct(school["assessment_completion_rate"]))
    cols[4].metric("Risk", school["risk_status"])
    st.dataframe(pd.DataFrame([school]), use_container_width=True)

elif page == "Assessment Outcomes":
    assessments = load_collection("assessments")
    students = load_collection("students")
    if assessments.empty or students.empty:
        st.warning("No assessment data found.")
        st.stop()
    joined = assessments.merge(students[["student_id", "gender", "school_id"]], on="student_id", how="left")
    st.plotly_chart(
        px.box(joined, x="assessment_type", y="score", color="gender"),
        use_container_width=True,
    )
    summary = joined.groupby(["assessment_type", "gender"], as_index=False)["score"].mean()
    st.dataframe(summary, use_container_width=True)

elif page == "Data Quality Monitor":
    if quality_df.empty:
        st.success("No data quality issues found.")
        st.stop()
    cols = st.columns(3)
    cols[0].metric("Issue Types", quality_df["issue_type"].nunique())
    cols[1].metric("Affected Collections", quality_df["collection"].nunique())
    cols[2].metric("Total Issues", int(quality_df["issue_count"].sum()))
    st.plotly_chart(
        px.bar(
            quality_df,
            x="collection",
            y="issue_count",
            color="severity",
            hover_data=["issue_type"],
        ),
        use_container_width=True,
    )
    st.dataframe(quality_df, use_container_width=True)
