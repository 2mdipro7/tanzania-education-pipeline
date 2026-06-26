from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_DATA = PROJECT_ROOT / "data" / "dashboard"


st.set_page_config(
    page_title="Mewaka Program Metrics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Common color mapping for risk status
RISK_COLORS = {
    "On Track": "#2ecc71",  # Green
    "Watch": "#f39c12",     # Orange
    "High Risk": "#e74c3c", # Red
    "Unknown": "#95a5a6"    # Gray
}


@st.cache_data
def load_collection(name: str) -> pd.DataFrame:
    """Load a collection from pre-exported static JSON files."""
    filepath = DASHBOARD_DATA / f"{name}.json"
    if not filepath.exists():
        return pd.DataFrame()
    with open(filepath, "r") as f:
        rows = json.load(f)
    return pd.DataFrame(rows)


def pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.1f}%"


def clean_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Format DataFrame column names to be reader-friendly."""
    if df.empty:
        return df
    return df.rename(columns=lambda x: str(x).replace("_", " ").title())


st.sidebar.title("🌍 Mewaka Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Overview",
        "Term 2 Performance",
        "School Map",
        "School Drilldown",
        "Assessment Outcomes",
        "Data Quality Monitor",
        "Pipeline Monitor",
    ],
)

school_df = load_collection("mart_school_performance")
regional_df = load_collection("mart_regional_summary")
overview_df = load_collection("mart_term2_overview")
quality_df = load_collection("mart_data_quality")


if page == "Executive Overview":
    st.title("Executive Overview")
    if overview_df.empty:
        st.warning("Run `python -m src.run_pipeline` to build dashboard marts.")
        st.stop()

    overview = overview_df.iloc[0]
    st.markdown("### Topline Metrics")
    cols = st.columns(6)
    cols[0].metric("Schools", int(overview.get("schools", 0)))
    cols[1].metric("Active Students", int(overview.get("active_students", 0)))
    cols[2].metric("Attendance", pct(overview.get("avg_attendance_rate")))
    cols[3].metric("Session Delivery", pct(overview.get("avg_session_delivery_rate")))
    cols[4].metric("Assessments", pct(overview.get("avg_assessment_completion_rate")))
    cols[5].metric("At-Risk Schools", int(overview.get("at_risk_schools", 0)))

    st.markdown("---")
    left, right = st.columns(2)
    with left:
        st.subheader("School Risk Distribution")
        if not school_df.empty:
            risk_counts = school_df["risk_status"].value_counts().reset_index()
            risk_counts.columns = ["risk_status", "schools"]
            fig = px.pie(
                risk_counts, 
                names="risk_status", 
                values="schools", 
                color="risk_status",
                color_discrete_map=RISK_COLORS,
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("District Attendance")
        if not regional_df.empty:
            fig = px.bar(
                regional_df.sort_values("avg_attendance_rate"),
                x="avg_attendance_rate",
                y="district",
                color="region",
                orientation="h",
            )
            fig.update_layout(xaxis_tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)

elif page == "Term 2 Performance":
    st.title("Term 2 Performance")
    if regional_df.empty:
        st.warning("No regional summary data found.")
        st.stop()
        
    metric = st.selectbox(
        "Select Metric to Visualize",
        [
            "avg_attendance_rate",
            "avg_session_delivery_rate",
            "avg_assessment_completion_rate",
        ],
        format_func=lambda x: x.replace("avg_", "").replace("_rate", "").title() + " Rate"
    )
    
    fig = px.bar(
        regional_df.sort_values(metric, ascending=False),
        x="district",
        y=metric,
        color="region",
        hover_data=["schools", "active_students", "at_risk_schools"],
    )
    fig.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(clean_cols(regional_df), use_container_width=True, hide_index=True)

elif page == "School Map":
    st.title("School Locations & Risk Status")
    if school_df.empty or "latitude" not in school_df.columns:
        st.warning("No school location data found.")
        st.stop()
        
    st.markdown("Interactive map showing school locations, colored by operational risk status and sized by student enrollment.")
    
    fig = px.scatter_mapbox(
        school_df,
        lat="latitude",
        lon="longitude",
        color="risk_status",
        size="active_students",
        hover_name="school_name",
        hover_data={
            "district": True,
            "attendance_rate": ":.1%",
            "session_delivery_rate": ":.1%",
            "latitude": False,
            "longitude": False
        },
        color_discrete_map=RISK_COLORS,
        zoom=5.5,
        center={"lat": -6.369, "lon": 34.888}, # Tanzania approximate center
        mapbox_style="open-street-map",
        height=600
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

elif page == "School Drilldown":
    st.title("School Drilldown")
    if school_df.empty:
        st.warning("No school mart data found.")
        st.stop()
        
    school_name = st.selectbox("Select School", school_df["school_name"].sort_values())
    school = school_df[school_df["school_name"] == school_name].iloc[0]
    
    st.markdown(f"### {school['school_name']} ({school['district']}, {school['region']})")
    
    cols = st.columns(5)
    cols[0].metric("Active Students", int(school.get("active_students", 0)))
    cols[1].metric("Attendance", pct(school.get("attendance_rate")))
    cols[2].metric("Session Delivery", pct(school.get("session_delivery_rate")))
    cols[3].metric("Assessments", pct(school.get("assessment_completion_rate")))
    cols[4].metric("Risk Status", school.get("risk_status"))
    
    st.markdown("#### Full Profile")
    profile_df = pd.DataFrame([school]).T.rename(columns={0: "Value"})
    profile_df.index = profile_df.index.str.replace("_", " ").str.title()
    st.dataframe(profile_df, use_container_width=True)

elif page == "Assessment Outcomes":
    st.title("Assessment Outcomes")
    assessments = load_collection("assessments")
    students = load_collection("students")
    if assessments.empty or students.empty:
        st.warning("No assessment data found.")
        st.stop()
        
    joined = assessments.merge(students[["student_id", "gender", "school_id"]], on="student_id", how="left")
    
    fig = px.box(
        joined, 
        x="assessment_type", 
        y="score", 
        color="gender",
        points="all",
        title="Score Distribution by Gender and Assessment Type"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### Average Scores")
    summary = joined.groupby(["assessment_type", "gender"], as_index=False)["score"].mean()
    summary["score"] = summary["score"].round(2)
    st.dataframe(clean_cols(summary), use_container_width=True, hide_index=True)

elif page == "Data Quality Monitor":
    st.title("Data Quality Monitor")
    if quality_df.empty:
        st.success("🎉 No data quality issues found in the latest pipeline run.")
        st.stop()
        
    st.markdown("Overview of data quality issues caught by the validation layer.")
    cols = st.columns(3)
    cols[0].metric("Issue Types", quality_df["issue_type"].nunique())
    cols[1].metric("Affected Collections", quality_df["collection"].nunique())
    cols[2].metric("Total Issues", int(quality_df["issue_count"].sum()))
    
    fig = px.bar(
        quality_df,
        x="collection",
        y="issue_count",
        color="severity",
        hover_data=["issue_type"],
        title="Issues by Collection",
        color_discrete_map={"high": "#e74c3c", "medium": "#f39c12", "low": "#f1c40f"}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### Issue Breakdown")
    st.dataframe(clean_cols(quality_df), use_container_width=True, hide_index=True)

elif page == "Pipeline Monitor":
    st.title("Pipeline Observability")
    runs_df = load_collection("pipeline_runs")
    batches_df = load_collection("raw_upload_batches")
    
    if runs_df.empty:
        st.info("No pipeline runs found.")
        st.stop()
        
    latest_run = runs_df.sort_values("started_at", ascending=False).iloc[0]
    run_id = latest_run.get("run_id", "N/A")
    status = latest_run.get("status", "Unknown")
    started = pd.to_datetime(latest_run.get("started_at")).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    st.markdown(f"**Latest Run:** `{run_id}` | **Status:** `{status}` | **Started:** `{started}`")
    
    metrics = latest_run.get("metrics", {})
    if isinstance(metrics, dict):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Records Generated", metrics.get("records_generated", 0))
        c2.metric("Records Loaded", metrics.get("records_loaded", 0))
        c3.metric("Quality Issues", metrics.get("quality_issues_found", 0))
        c4.metric("Contract Failures", metrics.get("contract_failures", 0))
    
    st.markdown("### Step Execution Details")
    steps = latest_run.get("steps", [])
    if isinstance(steps, list) and len(steps) > 0:
        steps_df = pd.DataFrame(steps)
        if "duration_seconds" in steps_df.columns:
            fig = px.bar(
                steps_df, 
                x="duration_seconds", 
                y="name", 
                orientation="h", 
                title="Duration by Step (s)",
                color="status",
                color_discrete_map={"success": "#2ecc71", "failed": "#e74c3c"}
            )
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(clean_cols(steps_df), use_container_width=True, hide_index=True)
        
    st.markdown("### Recent Upload Batches")
    if not batches_df.empty:
        display_cols = ["batch_id", "source_name", "loaded_records", "inserted_records", "updated_records", "unchanged_records", "ingested_at"]
        available_cols = [c for c in display_cols if c in batches_df.columns]
        display_df = batches_df.sort_values("ingested_at", ascending=False)[available_cols].head(20)
        st.dataframe(clean_cols(display_df), use_container_width=True, hide_index=True)
