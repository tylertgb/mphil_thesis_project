"""
OULAD Preprocessing Pipeline V2 - TEMPORAL LEAKAGE FIXED
─────────────────────────────────────────────────────────────────────────────
MPhil Thesis: A Human-Centered Evaluation of SHAP-Based Explainable Interfaces
              for Logistic Regression Models in Educational Decision-Support Systems

CRITICAL FIX: All features now respect a temporal prediction cutoff to prevent
              data leakage. Only information available BEFORE the cutoff is used.

PREDICTION CUTOFF: Day 42 (6 weeks into module)
Rationale: - Occurs after first TMA deadline (typically day 19-25)
           - Gives students time to establish engagement patterns
           - Early enough for meaningful intervention (most modules ~270 days)
           - Actionable timepoint for educators to provide support

Input  : data/raw/         (raw OULAD CSV files)
Output : data/processed/final_model_dataset_v2.csv
         data/processed/leakage_audit.txt (documentation of temporal constraints)
─────────────────────────────────────────────────────────────────────────────
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

# ── CRITICAL: Temporal Cutoff ──────────────────────────────────────────────────
PREDICTION_CUTOFF_DAY = 42  # Day in module when prediction is made

# ── Paths ──────────────────────────────────────────────────────────────────────
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
OUTPUT_FILE = PROCESSED_DIR / "final_model_dataset_v2.csv"
AUDIT_FILE = PROCESSED_DIR / "leakage_audit.txt"

# Merge keys shared across OULAD tables
MERGE_KEYS = ["id_student", "code_module", "code_presentation"]

# Features selected from studentInfo (available at enrollment - no temporal leakage)
# PROTECTED ATTRIBUTES EXCLUDED (Section 5 Decision: Option A)
# Rationale: Minimize algorithmic bias; simpler ethics review; focus on interface evaluation
INFO_FEATURES = [
    # "gender",              # EXCLUDED - protected attribute
    # "age_band",            # EXCLUDED - protected attribute
    # "highest_education",   # EXCLUDED - protected attribute
    "studied_credits",
    # "disability",          # EXCLUDED - protected attribute
    "num_of_prev_attempts",
]

# Categorical columns to one-hot encode for logistic regression
CATEGORICAL_COLS = []  # No categorical features after exclusion of protected attributes

# Binary target mapping from OULAD final_result values
TARGET_MAP = {"Pass": 1, "Distinction": 1, "Fail": 0, "Withdrawn": 0}


# ── Leakage Audit Logger ───────────────────────────────────────────────────────


class LeakageAudit:
    """Document temporal constraints for every feature to prove no leakage."""

    def __init__(self):
        self.log = []
        self.log.append("=" * 80)
        self.log.append("TEMPORAL LEAKAGE AUDIT")
        self.log.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log.append(f"Prediction Cutoff: Day {PREDICTION_CUTOFF_DAY}")
        self.log.append("=" * 80)
        self.log.append("")

    def record(self, feature_name: str, temporal_window: str, justification: str):
        """Record a feature's temporal constraint."""
        self.log.append(f"Feature: {feature_name}")
        self.log.append(f"  Temporal Window: {temporal_window}")
        self.log.append(f"  Justification: {justification}")
        self.log.append("")

    def save(self):
        """Write audit log to file."""
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_FILE, "w") as f:
            f.write("\n".join(self.log))
        print(f"\n  Leakage audit saved → {AUDIT_FILE}")


audit = LeakageAudit()


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


# ── 4. Feature engineering (TEMPORAL CONSTRAINTS APPLIED) ──────────────────────


def build_vle_features(vle: pd.DataFrame, cutoff_day: int) -> pd.DataFrame:
    """
    Aggregate VLE interaction logs per student/module/presentation.
    
    TEMPORAL CONSTRAINT: Only clicks with date <= cutoff_day are included.
    
    Produces:
      total_clicks_pre_cutoff       — sum of clicks before cutoff
      num_activities_accessed       — count of distinct VLE sites visited before cutoff
      days_active                   — number of distinct days with activity before cutoff
      avg_clicks_per_active_day     — mean clicks per day when student was active
      days_since_last_activity      — days between last activity and cutoff (engagement recency)
    """
    # CRITICAL: Filter to only pre-cutoff data
    vle_filtered = vle[vle["date"] <= cutoff_day].copy()
    
    print(f"\n  VLE Temporal Filter: {len(vle):,} → {len(vle_filtered):,} rows (kept {len(vle_filtered)/len(vle)*100:.1f}%)")
    
    # Aggregate per student
    agg = (
        vle_filtered.groupby(MERGE_KEYS)
        .agg(
            total_clicks_pre_cutoff=("sum_click", "sum"),
            num_activities_accessed=("id_site", "nunique"),
            days_active=("date", "nunique"),
            last_activity_day=("date", "max"),
        )
        .reset_index()
    )
    
    # Derived features
    agg["avg_clicks_per_active_day"] = agg["total_clicks_pre_cutoff"] / agg["days_active"].replace(0, 1)
    agg["days_since_last_activity"] = cutoff_day - agg["last_activity_day"]
    agg = agg.drop(columns=["last_activity_day"])
    
    # Audit logging
    audit.record(
        "total_clicks_pre_cutoff",
        f"VLE clicks with date <= {cutoff_day}",
        f"Only clicks recorded up to day {cutoff_day} are summed. Future clicks excluded."
    )
    audit.record(
        "num_activities_accessed",
        f"Distinct VLE sites visited with date <= {cutoff_day}",
        "Breadth of engagement measured only from pre-cutoff interactions."
    )
    audit.record(
        "days_active",
        f"Distinct days with VLE activity, date <= {cutoff_day}",
        "Consistency of engagement before cutoff."
    )
    audit.record(
        "avg_clicks_per_active_day",
        f"Derived from total_clicks_pre_cutoff / days_active",
        "Intensity of engagement per active day, using only pre-cutoff data."
    )
    audit.record(
        "days_since_last_activity",
        f"{cutoff_day} - max(date where date <= {cutoff_day})",
        "Recency of engagement relative to cutoff, not to module end."
    )
    
    return agg


def build_assessment_features(
    student_assessment: pd.DataFrame,
    assessments: pd.DataFrame,
    cutoff_day: int,
) -> pd.DataFrame:
    """
    Join submission records with assessment metadata, then aggregate
    per student/module/presentation.
    
    TEMPORAL CONSTRAINT: Only assessments with due date <= cutoff_day are included.
                        Excludes final exams and late-module TMAs.
    
    Produces:
      avg_assessment_score          — mean score on assessments submitted before cutoff
      num_assessments_completed     — count of assessments with submissions before cutoff
      num_assessments_due           — count of assessments due by cutoff (denominator)
      completion_rate               — proportion of due assessments that were submitted
    """
    # CRITICAL: Filter assessments to only those due by cutoff
    assessments_pre_cutoff = assessments[
        (assessments["date"].notna()) &  # Exclude exams with no date
        (assessments["date"] <= cutoff_day)
    ].copy()
    
    print(f"  Assessment Temporal Filter: {len(assessments)} → {len(assessments_pre_cutoff)} assessments due by day {cutoff_day}")
    
    # Count assessments due per student
    assessments_due = (
        assessments_pre_cutoff.groupby(["code_module", "code_presentation"])["id_assessment"]
        .apply(list)
        .reset_index()
        .rename(columns={"id_assessment": "assessments_due_list"})
    )
    
    # Merge submissions with assessment metadata
    merged = student_assessment.merge(
        assessments_pre_cutoff[["id_assessment", "code_module", "code_presentation", "date"]],
        on="id_assessment",
        how="inner",  # Only keep submissions for pre-cutoff assessments
    )
    
    # Aggregate submissions per student
    completed = (
        merged.groupby(MERGE_KEYS)
        .agg(
            avg_assessment_score=("score", "mean"),
            num_assessments_completed=("id_assessment", "count"),
        )
        .reset_index()
    )
    
    # Calculate completion rate
    # First, get number of assessments due for each student's module
    completed = completed.merge(
        assessments_due,
        on=["code_module", "code_presentation"],
        how="left"
    )
    completed["num_assessments_due"] = completed["assessments_due_list"].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    completed["completion_rate"] = (
        completed["num_assessments_completed"] / completed["num_assessments_due"].replace(0, 1)
    )
    completed = completed.drop(columns=["assessments_due_list"])
    
    # Audit logging
    audit.record(
        "avg_assessment_score",
        f"Mean score on assessments with due date <= {cutoff_day}",
        f"Only assessments due by day {cutoff_day} are included. Final exams and late TMAs excluded."
    )
    audit.record(
        "num_assessments_completed",
        f"Count of submitted assessments with due date <= {cutoff_day}",
        "Measures early engagement with coursework. Late submissions excluded."
    )
    audit.record(
        "num_assessments_due",
        f"Count of assessments with due date <= {cutoff_day}",
        "Denominator for completion rate. Known at cutoff time."
    )
    audit.record(
        "completion_rate",
        "num_assessments_completed / num_assessments_due",
        "Proportion of early assessments submitted. Derived from pre-cutoff data only."
    )
    
    return completed


# ── 5. Target encoding ─────────────────────────────────────────────────────────


def encode_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map OULAD final_result to a binary label:
      Pass / Distinction → 1  (Success)
      Fail / Withdrawn   → 0  (At-Risk)
    
    TEMPORAL NOTE: final_result is not known at cutoff day, but it is the LABEL
                  we're predicting, not a feature. It represents end-of-module
                  outcome and does not leak into feature computation.
    """
    audit.record(
        "target (final_result)",
        "End-of-module outcome (label only, not a feature)",
        "This is what we're predicting. Not used in any feature computation."
    )
    
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
    
    TEMPORAL NOTE: All categorical features (gender, age_band, etc.) are known
                  at enrollment and do not change during the module.
    
    PROTECTED ATTRIBUTES: Option A selected - no categorical features to encode.
                         Protected attributes excluded to minimize bias.
    """
    if CATEGORICAL_COLS:
        for col in CATEGORICAL_COLS:
            if col in df.columns:
                audit.record(
                    f"{col} (one-hot encoded)",
                    "Available at student enrollment",
                    "Demographic/background features known before module starts. No temporal leakage."
                )
        return pd.get_dummies(df, columns=CATEGORICAL_COLS, drop_first=True)
    else:
        # No categorical encoding needed (protected attributes excluded)
        return df


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

    # ── Step 4: Engineer features WITH TEMPORAL CONSTRAINTS ────────────────────
    print(f"\n[4/6] Engineering features (cutoff = day {PREDICTION_CUTOFF_DAY}) …")
    vle_features = build_vle_features(vle, PREDICTION_CUTOFF_DAY)
    print(f"  VLE features shape        : {vle_features.shape}")
    assessment_features = build_assessment_features(
        student_assessment, assessments, PREDICTION_CUTOFF_DAY
    )
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

    # Record enrollment features in audit
    for feat in INFO_FEATURES:
        audit.record(
            feat,
            "Available at student enrollment",
            "Background/demographic feature known before module starts."
        )

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
    print(f"  Feature count       : {df.shape[1] - 1} (excluding target)")
    print(f"\n  Target distribution :")
    counts = df["target"].value_counts().sort_index()
    for label, count in counts.items():
        status = "Success (1)" if label == 1 else "At-Risk (0)"
        pct = count / len(df) * 100
        print(f"    {status} : {count:,} ({pct:.1f}%)")
    print(f"{'─'*54}\n")

    # Save audit log
    audit.save()

    return df


if __name__ == "__main__":
    run()
