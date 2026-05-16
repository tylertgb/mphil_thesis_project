"""
Shared student input form and feature encoder.
Used identically by both Variant A and Variant B to ensure parity.
"""

import pandas as pd
import streamlit as st


# Raw options matching OULAD domain values
GENDER_OPTIONS = ["Female", "Male"]
AGE_BAND_OPTIONS = ["0-35", "35-55", "55<="]
EDUCATION_OPTIONS = [
    "A Level or Equivalent",
    "HE Qualification",
    "Lower Than A Level",
    "No Formal quals",
    "Post Graduate Qualification",
]
DISABILITY_OPTIONS = ["No", "Yes"]


def render_form() -> dict:
    """
    Render the student profile input form.
    Returns a dict of raw (human-readable) field values.
    """
    st.subheader("Student Profile")

    col1, col2 = st.columns(2)

    with col1:
        gender = st.selectbox("Gender", GENDER_OPTIONS)
        age_band = st.selectbox("Age Band", AGE_BAND_OPTIONS)
        highest_education = st.selectbox("Highest Education", EDUCATION_OPTIONS)
        disability = st.selectbox("Disability", DISABILITY_OPTIONS)

    with col2:
        studied_credits = st.number_input(
            "Credits Studied", min_value=0, max_value=600, value=120, step=10
        )
        avg_assessment_score = st.number_input(
            "Avg. Assessment Score", min_value=0.0, max_value=100.0, value=60.0, step=0.5
        )
        num_assessments_completed = st.number_input(
            "Assessments Completed", min_value=0, max_value=50, value=5, step=1
        )
        total_clicks = st.number_input(
            "Total VLE Clicks", min_value=0, max_value=100000, value=1000, step=50
        )
        num_activities_accessed = st.number_input(
            "Activities Accessed", min_value=0, max_value=500, value=20, step=1
        )

    return {
        "gender": gender,
        "age_band": age_band,
        "highest_education": highest_education,
        "disability": disability,
        "studied_credits": studied_credits,
        "avg_assessment_score": avg_assessment_score,
        "num_assessments_completed": num_assessments_completed,
        "total_clicks": total_clicks,
        "num_activities_accessed": num_activities_accessed,
    }


def encode_input(raw: dict, feature_names: list[str]) -> pd.DataFrame:
    """
    Convert raw form values into the one-hot encoded feature vector
    expected by the trained model (matches preprocessing.py encoding).
    """
    row = {f: 0 for f in feature_names}

    # Numeric features — pass through directly
    row["studied_credits"] = raw["studied_credits"]
    row["avg_assessment_score"] = raw["avg_assessment_score"]
    row["num_assessments_completed"] = raw["num_assessments_completed"]
    row["total_clicks"] = raw["total_clicks"]
    row["num_activities_accessed"] = raw["num_activities_accessed"]

    # One-hot encoded categoricals (drop_first=True baseline categories):
    #   gender           → baseline: Female
    #   age_band         → baseline: 0-35
    #   highest_education → baseline: A Level or Equivalent
    #   disability       → baseline: No

    if raw["gender"] == "Male" and "gender_M" in row:
        row["gender_M"] = 1

    if raw["age_band"] == "35-55" and "age_band_35-55" in row:
        row["age_band_35-55"] = 1
    elif raw["age_band"] == "55<=" and "age_band_55<=" in row:
        row["age_band_55<="] = 1

    edu_map = {
        "HE Qualification": "highest_education_HE Qualification",
        "Lower Than A Level": "highest_education_Lower Than A Level",
        "No Formal quals": "highest_education_No Formal quals",
        "Post Graduate Qualification": "highest_education_Post Graduate Qualification",
    }
    edu_col = edu_map.get(raw["highest_education"])
    if edu_col and edu_col in row:
        row[edu_col] = 1

    if raw["disability"] == "Yes" and "disability_Y" in row:
        row["disability_Y"] = 1

    return pd.DataFrame([row])[feature_names]
