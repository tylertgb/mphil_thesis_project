"""
OULAD Preprocessing Pipeline
─────────────────────────────────────────────────────────────────────────────
MPhil Thesis: A Human-Centered Evaluation of SHAP-Based Explainable Interfaces
              for Logistic Regression Models in Educational Decision-Support Systems

Input  : data/raw/         (raw OULAD CSV files)
Output : data/processed/final_model_dataset.csv
─────────────────────────────────────────────────────────────────────────────
"""

import numpy as np
import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
OUTPUT_FILE = PROCESSED_DIR / "final_model_dataset.csv"

# Merge keys shared across OULAD tables
MERGE_KEYS = ["id_student", "code_module", "code_presentation"]

# Features selected from studentInfo
INFO_FEATURES = [
    "gender",
    "age_band",
    "highest_education",
    "studied_credits",
    "disability",
]

# Categorical columns to one-hot encode for logistic regression
CATEGORICAL_COLS = ["gender", "age_band", "highest_education", "disability"]

# Binary target mapping from OULAD final_result values
TARGET_MAP = {"Pass": 1, "Distinction": 1, "Fail": 0, "Withdrawn": 0}


# ── 1. Loaders ─────────────────────────────────────────────────────────────────


def load_csv(filename: str) -> pd.DataFrame:
    """Load a single CSV from the raw data directory."""
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Expected file not found: {path}")
    df = pd.read_csv(path)
    print(f"  Loaded {filename:<40} → {df.shape[0]:>7,} rows, {df.shape[1]} cols")
    return df


def load_student_vle() -> pd.DataFrame:
    """Concatenate studentVle_0.csv … studentVle_7.csv into one DataFrame."""
    chunks = []
    for i in range(8):
        fname = f"studentVle_{i}.csv"
        path = RAW_DIR / fname
        if path.exists():
            chunks.append(pd.read_csv(path))
        else:
            print(f"  [warn] {fname} not found — skipping")

    if not chunks:
        raise FileNotFoundError("No studentVle_*.csv files found in data/raw/")

    combined = pd.concat(chunks, ignore_index=True)
    print(f"  Combined studentVle ({len(chunks)} files)           → {combined.shape[0]:>7,} rows, {combined.shape[1]} cols")
    return combined


# ── 2. Inspection ──────────────────────────────────────────────────────────────


def inspect(df: pd.DataFrame, name: str) -> None:
    """Print a quality summary: missing values, duplicates, and dtypes."""
    divider = "─" * 54
    print(f"\n{divider}")
    print(f"  {name}  |  shape: {df.shape}")
    print(divider)

    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        print("  Missing values : none")
    else:
        print("  Missing values :")
        for col, count in missing.items():
            pct = count / len(df) * 100
            print(f"    {col:<35} {count:>6,} ({pct:.1f}%)")

    dups = df.duplicated().sum()
    print(f"  Duplicate rows : {dups:,}")
    print("  dtypes         :")
    for col, dtype in df.dtypes.items():
        print(f"    {col:<35} {str(dtype)}")


# ── 3. Missing-value imputation ────────────────────────────────────────────────


def impute(df: pd.DataFrame) -> pd.DataFrame:
    """
    Numerical columns  → median imputation
    Categorical columns → fill with 'Unknown'
    """
    for col in df.columns:
        if df[col].isnull().any():
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna("Unknown")
    return df


# ── 4. Feature engineering ─────────────────────────────────────────────────────


def build_vle_features(vle: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate VLE interaction logs per student/module/presentation.

    Produces:
      total_clicks            — total number of clicks across all VLE resources
      num_activities_accessed — count of distinct VLE activity sites visited
    """
    return (
        vle.groupby(MERGE_KEYS)
        .agg(
            total_clicks=("sum_click", "sum"),
            num_activities_accessed=("id_site", "nunique"),
        )
        .reset_index()
    )


def build_assessment_features(
    student_assessment: pd.DataFrame,
    assessments: pd.DataFrame,
) -> pd.DataFrame:
    """
    Join submission records with assessment metadata, then aggregate
    per student/module/presentation.

    Produces:
      avg_assessment_score    — mean score across all submitted assessments
      num_assessments_completed — count of submitted assessments
    """
    merged = student_assessment.merge(
        assessments[["id_assessment", "code_module", "code_presentation"]],
        on="id_assessment",
        how="left",
    )
    return (
        merged.groupby(MERGE_KEYS)
        .agg(
            avg_assessment_score=("score", "mean"),
            num_assessments_completed=("id_assessment", "count"),
        )
        .reset_index()
    )


# ── 5. Target encoding ─────────────────────────────────────────────────────────


def encode_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map OULAD final_result to a binary label:
      Pass / Distinction → 1  (Success)
      Fail / Withdrawn   → 0  (At-Risk)
    """
    df["target"] = df["final_result"].map(TARGET_MAP)
    unmapped = df["target"].isnull().sum()
    if unmapped > 0:
        print(f"  [warn] {unmapped:,} rows had unmappable final_result values — will be dropped")
    return df


# ── 6. Categorical encoding ────────────────────────────────────────────────────


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    One-hot encode categorical features.
    drop_first=True avoids the dummy-variable trap for logistic regression.
    """
    return pd.get_dummies(df, columns=CATEGORICAL_COLS, drop_first=True)


# ── 7. Main pipeline ───────────────────────────────────────────────────────────


def run() -> pd.DataFrame:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Load ────────────────────────────────────────────────────────────
    print("\n[1/6] Loading raw OULAD tables …")
    student_info = load_csv("studentInfo.csv")
    student_assessment = load_csv("studentAssessment.csv")
    assessments = load_csv("assessments.csv")
    vle = load_student_vle()

    # ── Step 2: Inspect ─────────────────────────────────────────────────────────
    print("\n[2/6] Inspecting datasets …")
    inspect(student_info, "studentInfo")
    inspect(student_assessment, "studentAssessment")
    inspect(assessments, "assessments")
    inspect(vle, "studentVle (combined)")

    # ── Step 3: Impute ──────────────────────────────────────────────────────────
    print("\n[3/6] Imputing missing values …")
    student_info = impute(student_info)
    student_assessment = impute(student_assessment)
    assessments = impute(assessments)
    vle = impute(vle)
    print("  Imputation complete.")

    # ── Step 4: Engineer features ───────────────────────────────────────────────
    print("\n[4/6] Engineering features …")
    vle_features = build_vle_features(vle)
    print(f"  VLE features shape        : {vle_features.shape}")
    assessment_features = build_assessment_features(student_assessment, assessments)
    print(f"  Assessment features shape : {assessment_features.shape}")

    # ── Step 5: Merge ───────────────────────────────────────────────────────────
    print("\n[5/6] Merging tables …")
    info_cols = MERGE_KEYS + INFO_FEATURES + ["final_result"]

    df = (
        student_info[info_cols]
        .merge(assessment_features, on=MERGE_KEYS, how="left")
        .merge(vle_features, on=MERGE_KEYS, how="left")
    )
    print(f"  Merged dataset shape : {df.shape}")

    # Encode binary target, drop rows with unknown result, remove source column
    df = encode_target(df)
    df = df.dropna(subset=["target"])
    df["target"] = df["target"].astype(int)
    df = df.drop(columns=["final_result"])

    # One-hot encode categoricals, drop merge keys (not model inputs)
    df = encode_categoricals(df)
    df = df.drop(columns=MERGE_KEYS)

    # ── Step 6: Save ────────────────────────────────────────────────────────────
    print(f"\n[6/6] Saving → {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n{'─'*54}")
    print(f"  Final dataset shape : {df.shape}")
    print(f"  Columns             : {list(df.columns)}")
    print(f"\n  Target distribution :")
    counts = df["target"].value_counts().sort_index()
    for label, count in counts.items():
        status = "Success (1)" if label == 1 else "At-Risk (0)"
        pct = count / len(df) * 100
        print(f"    {status} : {count:,} ({pct:.1f}%)")
    print(f"{'─'*54}\n")

    return df


if __name__ == "__main__":
    run()
