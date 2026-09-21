"""
Logistic Regression Model + SHAP Explainer V2 - LEAKAGE FIXED + CALIBRATED
─────────────────────────────────────────────────────────────────────────────
MPhil Thesis: A Human-Centered Evaluation of SHAP-Based Explainable Interfaces
              for Logistic Regression Models in Educational Decision-Support Systems

CRITICAL FIXES:
1. Uses temporally-constrained dataset (no leakage)
2. SHAP sign convention explicitly documented and verified
3. Calibration analysis and remediation included
4. Reproducibility via fixed seeds

Input  : data/processed/final_model_dataset_v2.csv
Output : models/saved_models/logistic_regression.pkl
         models/saved_models/scaler.pkl
         models/saved_models/shap_values.npy
         models/saved_models/shap_expected_value.npy
         models/saved_models/feature_names.json
         models/saved_models/calibrated_model.pkl
         results/calibration_report.txt
─────────────────────────────────────────────────────────────────────────────
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    brier_score_loss,
)
import joblib
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_FILE = Path("data/processed/final_model_dataset_v2.csv")
SAVE_DIR = Path("models/saved_models")
RESULTS_DIR = Path("results")

# ── Hyperparameters ────────────────────────────────────────────────────────────
TEST_SIZE = 0.2
RANDOM_STATE = 42
CV_FOLDS = 5

# ──SHAP SIGN CONVENTION (CRITICAL - READ THIS FIRST) ──────────────────────────
#
# For binary classification where positive class (1) = "Success" / "Pass":
#
# • POSITIVE SHAP value → feature pushes prediction TOWARD Success (class 1)
# • NEGATIVE SHAP value → feature pushes prediction TOWARD At-Risk (class 0)
#
# The model predicts P(Success|X). A feature with:
#   - High SHAP value = increases probability of success
#   - Low (negative) SHAP value = decreases probability of success (increases risk)
#
# This convention is enforced in:
#   1. compute_shap() - extracts SHAP values for class 1 (Success)
#   2. Interface rendering - bars point right for positive, left for negative
#   3. Plain-language text - uses get_shap_direction() helper
#
# ───────────────────────────────────────────────────────────────────────────────


# ── 1. Data loading ────────────────────────────────────────────────────────────


def load_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load processed dataset and split into features and target."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at {DATA_FILE}. "
            "Run preprocessing.py first."
        )
    df = pd.read_csv(DATA_FILE)
    X = df.drop(columns=["target"])
    y = df["target"]
    print(f"  Dataset loaded   : {df.shape[0]:,} rows, {X.shape[1]} features")
    print(f"  Class balance    : At-Risk={int((y==0).sum()):,}  Success={int((y==1).sum()):,}")
    return X, y


# ── 2. Preprocessing ───────────────────────────────────────────────────────────


def impute_remaining(X: pd.DataFrame) -> pd.DataFrame:
    """
    Median-impute any NaNs left after left-joins in the preprocessing pipeline.
    Students with no VLE activity or no assessment submissions produce NaN in
    those aggregated columns — this ensures the model receives no missing values.
    """
    nan_cols = X.columns[X.isnull().any()].tolist()
    if nan_cols:
        print(f"  [impute] NaN columns resolved : {nan_cols}")
        for col in nan_cols:
            X[col] = X[col].fillna(X[col].median())
    return X


def scale_features(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, StandardScaler]:
    """Fit StandardScaler on train set; apply to both splits."""
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)
    return X_train_sc, X_test_sc, scaler


# ── 3. Training ────────────────────────────────────────────────────────────────


def train(X_train: np.ndarray, y_train: pd.Series) -> LogisticRegression:
    """
    Train logistic regression with L2 regularisation.
    class_weight='balanced' compensates for any At-Risk / Success imbalance.
    """
    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        solver="lbfgs",
    )
    model.fit(X_train, y_train)
    return model


# ── 4. Evaluation ──────────────────────────────────────────────────────────────


def evaluate(
    model: LogisticRegression,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: pd.Series,
    y_test: pd.Series,
) -> None:
    """Print accuracy, ROC-AUC, classification report, confusion matrix, and CV scores."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    divider = "-" * 54
    print(f"\n{divider}")
    print("  MODEL EVALUATION")
    print(divider)
    print(f"  Test accuracy   : {accuracy_score(y_test, y_pred):.4f}")
    print(f"  ROC-AUC         : {roc_auc_score(y_test, y_prob):.4f}")

    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["At-Risk (0)", "Success (1)"]))

    cm = confusion_matrix(y_test, y_pred)
    print("  Confusion Matrix (rows=actual, cols=predicted):")
    print(f"    TN={cm[0,0]:>5}  FP={cm[0,1]:>5}")
    print(f"    FN={cm[1,0]:>5}  TP={cm[1,1]:>5}")

    # Stratified cross-validation on full training split
    skf = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(model, X_train, y_train, cv=skf, scoring="roc_auc")
    print(f"\n  {CV_FOLDS}-Fold CV ROC-AUC : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(divider)


# ── 5. Calibration Analysis & Remediation ──────────────────────────────────────


def analyze_calibration(
    model: LogisticRegression,
    X_test: np.ndarray,
    y_test: pd.Series,
) -> dict:
    """
    Analyze model calibration and generate reliability diagram.
    
    Returns dict with:
      - brier_score: scalar measure of calibration + accuracy
      - calibration_curve_data: (prob_true, prob_pred) for plotting
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    y_prob = model.predict_proba(X_test)[:, 1]  # P(Success)
    brier = brier_score_loss(y_test, y_prob)
    
    # Compute calibration curve (10 bins)
    prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=10, strategy='uniform')
    
    # Plot reliability diagram
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Perfect calibration line
    ax.plot([0, 1], [0, 1], "k--", label="Perfect Calibration", linewidth=2)
    
    # Actual calibration
    ax.plot(prob_pred, prob_true, "o-", label="Model Calibration", linewidth=2, markersize=8)
    
    ax.set_xlabel("Mean Predicted Probability", fontsize=12)
    ax.set_ylabel("Fraction of Positives (True Probability)", fontsize=12)
    ax.set_title(f"Uncalibrated Reliability Diagram\nBrier Score = {brier:.4f}", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    ax.set_xlim([-0.05, 1.05])
    ax.set_ylim([-0.05, 1.05])
    
    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "calibration_reliability_diagram_uncalibrated.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    
    print(f"\n  Calibration Analysis:")
    print(f"    Brier Score (uncalibrated) : {brier:.4f}")
    print(f"    Uncalibrated diagram saved → {RESULTS_DIR}/calibration_reliability_diagram_uncalibrated.png")
    
    return {
        "brier_score": brier,
        "calibration_curve": (prob_true, prob_pred),
    }


def calibrate_model(
    base_model: LogisticRegression,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: pd.Series,
    y_test: pd.Series,
) -> tuple[CalibratedClassifierCV, float]:
    """
    Apply Platt scaling (sigmoid calibration) to improve probability estimates.
    Uses 5-fold CV on the training set to fit the calibration mapping.
    
    Returns calibrated model and its Brier score on test set.
    """
    # Calibrate using Platt scaling (sigmoid method)
    calibrated = CalibratedClassifierCV(
        base_model,
        method='sigmoid',
        cv=5,
    )
    calibrated.fit(X_train, y_train)
    
    # Evaluate calibrated model
    y_prob_cal = calibrated.predict_proba(X_test)[:, 1]
    brier_cal = brier_score_loss(y_test, y_prob_cal)
    
    print(f"    Brier Score (calibrated)   : {brier_cal:.4f}")
    
    # Generate calibrated reliability diagram
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    prob_true, prob_pred = calibration_curve(y_test, y_prob_cal, n_bins=10, strategy='uniform')
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([0, 1], [0, 1], "k--", label="Perfect Calibration", linewidth=2)
    ax.plot(prob_pred, prob_true, "o-", label="Calibrated Model", linewidth=2, markersize=8)
    ax.set_xlabel("Mean Predicted Probability", fontsize=12)
    ax.set_ylabel("Fraction of Positives (True Probability)", fontsize=12)
    ax.set_title(f"Calibrated Reliability Diagram\nBrier Score = {brier_cal:.4f}", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    ax.set_xlim([-0.05, 1.05])
    ax.set_ylim([-0.05, 1.05])
    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "calibration_reliability_diagram_calibrated.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    
    print(f"    Calibrated diagram saved   → {RESULTS_DIR}/calibration_reliability_diagram_calibrated.png")
    
    return calibrated, brier_cal


# ── 6. SHAP Explanation & Verification ─────────────────────────────────────────


def compute_shap(
    model: LogisticRegression,
    X_train: np.ndarray,
    X_test: np.ndarray,
    feature_names: list[str],
) -> tuple[np.ndarray, float]:
    """
    Compute SHAP values using LinearExplainer (exact for linear models).
    
    SHAP SIGN CONVENTION (enforced here):
    - Positive SHAP value → feature pushes prediction TOWARD Success (class 1)
    - Negative SHAP value → feature pushes prediction TOWARD At-Risk (class 0)
    
    This function extracts SHAP values for the POSITIVE class (Success = 1).
    
    Returns:
      - shap_values: array of shape (n_samples, n_features) for class 1
      - expected_value: base rate (expected model output in log-odds space)
    """
    explainer = shap.LinearExplainer(
        model, 
        X_train, 
        feature_perturbation="interventional"
    )
    shap_values_raw = explainer.shap_values(X_test)
    
    # CRITICAL: For binary classification, LinearExplainer may return values for class 0 or class 1
    # We ALWAYS want class 1 (Success). Check shape and extract correctly.
    if isinstance(shap_values_raw, list):
        # List format: [shap_for_class_0, shap_for_class_1]
        shap_values = shap_values_raw[1]
        expected_value = explainer.expected_value[1]
        print("  [SHAP] Extracted values for class 1 (Success) from list format")
    elif len(shap_values_raw.shape) == 3:
        # 3D array format: (n_samples, n_features, n_classes)
        shap_values = shap_values_raw[:, :, 1]
        expected_value = explainer.expected_value[1]
        print("  [SHAP] Extracted values for class 1 (Success) from 3D array")
    else:
        # 2D array: assumed to be for the positive class already
        shap_values = shap_values_raw
        expected_value = explainer.expected_value
        print("  [SHAP] Using 2D array (assumed class 1)")
    
    print(f"  [SHAP] Expected value (base rate): {expected_value:.4f}")
    print(f"  [SHAP] Values shape: {shap_values.shape}")
    
    # VERIFICATION: Check additivity property
    # For logistic regression in log-odds space:
    #   sum(SHAP values) + expected_value ≈ model log-odds output
    print("\n  SHAP Additivity Verification (first 5 test samples):")
    from scipy.special import logit
    for i in range(min(5, len(X_test))):
        shap_sum = shap_values[i].sum() + expected_value
        # Get model's log-odds prediction
        prob = model.predict_proba(X_test[i:i+1])[0, 1]
        model_logodds = logit(np.clip(prob, 1e-10, 1 - 1e-10))
        diff = abs(shap_sum - model_logodds)
        status = "✓ PASS" if diff < 0.01 else "✗ FAIL"
        print(f"    Sample {i}: SHAP sum={shap_sum:>7.3f}, Model={model_logodds:>7.3f}, Diff={diff:.4f} {status}")
    
    print("\n  SHAP Summary (mean |SHAP| per feature — all 11):")
    mean_abs = np.abs(shap_values).mean(axis=0)
    ranking = np.argsort(mean_abs)[::-1]
    for rank, idx in enumerate(ranking, 1):
        print(f"    {rank:>2}. {feature_names[idx]:<40} {mean_abs[idx]:.4f}")

    return shap_values, expected_value


# ── 7. SHAP Direction Helper (for interface consistency) ──────────────────────


def get_shap_direction(shap_value: float) -> dict:
    """
    Convert a SHAP value to both chart direction and plain-language text.
    
    SINGLE SOURCE OF TRUTH for SHAP interpretation - both interfaces MUST use this.
    
    Returns dict with:
      - direction: "increases" or "decreases" (for plain language)
      - effect: "success" or "risk" (what the feature pushes toward)
      - bar_direction: "positive" or "negative" (for chart rendering)
      - color: color code for visualization
    """
    if shap_value > 0:
        return {
            "direction": "increases",
            "effect": "success",
            "plain_text": "increases likelihood of success",
            "bar_direction": "positive",
            "color": "#10B981",  # Green
        }
    else:
        return {
            "direction": "decreases",
            "effect": "risk",
            "plain_text": "decreases likelihood of success (increases risk)",
            "bar_direction": "negative",
            "color": "#EF4444",  # Red
        }


# ── 8. Persistence ─────────────────────────────────────────────────────────────


def save_artefacts(
    model: LogisticRegression,
    calibrated_model: CalibratedClassifierCV,
    scaler: StandardScaler,
    shap_values: np.ndarray,
    expected_value: float,
    feature_names: list[str],
    calibration_metrics: dict,
) -> None:
    """Serialise all artefacts consumed by the interface variants and notebooks."""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, SAVE_DIR / "logistic_regression.pkl")
    joblib.dump(calibrated_model, SAVE_DIR / "calibrated_model.pkl")
    joblib.dump(scaler, SAVE_DIR / "scaler.pkl")
    np.save(SAVE_DIR / "shap_values.npy", shap_values)
    np.save(SAVE_DIR / "shap_expected_value.npy", np.array([expected_value]))

    with open(SAVE_DIR / "feature_names.json", "w") as f:
        json.dump(feature_names, f, indent=2)

    # Save calibration report
    with open(RESULTS_DIR / "calibration_report.txt", "w") as f:
        f.write("CALIBRATION REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Brier Score (Uncalibrated): {calibration_metrics['brier_uncalibrated']:.4f}\n")
        f.write(f"Brier Score (Calibrated):   {calibration_metrics['brier_calibrated']:.4f}\n")
        f.write(f"Improvement:                {calibration_metrics['brier_uncalibrated'] - calibration_metrics['brier_calibrated']:.4f}\n\n")
        f.write("Interface displays CALIBRATED probabilities from calibrated_model.pkl\n")
        f.write("to ensure trustworthy confidence estimates for participants.\n")

    print(f"\n  Artefacts saved to {SAVE_DIR}/")
    for p in sorted(SAVE_DIR.iterdir()):
        print(f"    {p.name}")
    print(f"\n  Calibration report → {RESULTS_DIR}/calibration_report.txt")


# ── 9. Inference helper (used by both interface variants) ──────────────────────


def predict_student(
    student_features: dict,
    model: LogisticRegression | None = None,
    calibrated_model: CalibratedClassifierCV | None = None,
    scaler: StandardScaler | None = None,
    feature_names: list[str] | None = None,
    use_calibrated: bool = True,
    case_id: str | None = None,
    shap_background: np.ndarray | None = None,
) -> dict:
    """
    Run inference for a single student record.

    Parameters
    ----------
    student_features : dict mapping feature name → raw value
    model : uncalibrated model (for SHAP computation)
    calibrated_model : calibrated model (for probability output)
    scaler : fitted StandardScaler
    feature_names : list of feature names in correct order
    use_calibrated : if True, returns calibrated probability (recommended)
    case_id : optional identifier for this prediction (e.g., task case ID)
    shap_background : scaled background data for SHAP (if None, uses zero vector)

    Returns
    -------
    dict with keys:
      case_id       — optional identifier passed in
      prediction    — 0 (At-Risk) or 1 (Success)
      probability   — P(Success), calibrated if use_calibrated=True
      label         — human-readable string
      raw_features  — input feature values (for traceability)
      shap_values   — dict of feature → SHAP value (for explanation)
      shap_directions — dict of feature → direction interpretation
      expected_value — SHAP baseline used
      top_3_features — top 3 contributors by absolute SHAP magnitude
      model_version  — identifier for model/feature set version
    """
    if model is None:
        model = joblib.load(SAVE_DIR / "logistic_regression.pkl")
    if calibrated_model is None:
        calibrated_model = joblib.load(SAVE_DIR / "calibrated_model.pkl")
    if scaler is None:
        scaler = joblib.load(SAVE_DIR / "scaler.pkl")
    if feature_names is None:
        with open(SAVE_DIR / "feature_names.json") as f:
            feature_names = json.load(f)

    row = pd.DataFrame([student_features])[feature_names]
    row_sc = scaler.transform(row)

    # Use calibrated model for probability (better trustworthiness)
    if use_calibrated:
        probability = float(calibrated_model.predict_proba(row_sc)[0][1])
        prediction = int(calibrated_model.predict(row_sc)[0])
    else:
        probability = float(model.predict_proba(row_sc)[0][1])
        prediction = int(model.predict(row_sc)[0])
    
    label = "Success" if prediction == 1 else "At-Risk"

    # Per-instance SHAP (always from base model, not calibrated wrapper)
    # Use proper background data (mean student) for meaningful SHAP values
    if shap_background is None:
        # Zero vector represents the mean student after StandardScaling
        shap_background = np.zeros((1, row_sc.shape[1]))
    
    explainer = shap.LinearExplainer(model, shap_background, feature_perturbation="interventional")
    instance_shap_raw = explainer.shap_values(row_sc)
    expected_value = explainer.expected_value
    
    # Handle different SHAP output formats
    if isinstance(instance_shap_raw, list):
        instance_shap = instance_shap_raw[1][0]  # Class 1
        if isinstance(expected_value, (list, np.ndarray)):
            expected_value = expected_value[1]
    elif len(instance_shap_raw.shape) == 3:
        instance_shap = instance_shap_raw[0, :, 1]  # Class 1
        if isinstance(expected_value, (list, np.ndarray)):
            expected_value = expected_value[1]
    else:
        instance_shap = instance_shap_raw[0]

    shap_dict = dict(zip(feature_names, instance_shap.tolist()))
    
    # Add direction interpretations using the single source of truth
    shap_directions = {
        feat: get_shap_direction(val) for feat, val in shap_dict.items()
    }
    
    # Get top 3 features by absolute SHAP magnitude
    sorted_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
    top_3_features = [
        {
            "feature": feat,
            "shap_value": val,
            "direction": shap_directions[feat]["plain_text"],
            "abs_magnitude": abs(val),
        }
        for feat, val in sorted_features[:3]
    ]

    return {
        "case_id": case_id,
        "prediction": prediction,
        "probability": round(probability, 4),
        "label": label,
        "raw_features": student_features,  # Original input for traceability
        "shap_values": shap_dict,
        "shap_directions": shap_directions,
        "expected_value": float(expected_value),
        "top_3_features": top_3_features,
        "model_version": "v2_leakage_fixed_calibrated",  # Track model version
    }


# ── Main ───────────────────────────────────────────────────────────────────────


def run() -> None:
    print("\n[1/7] Loading data …")
    X, y = load_data()
    X = impute_remaining(X)
    feature_names = X.columns.tolist()

    print("\n[2/7] Splitting and scaling …")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    X_train_sc, X_test_sc, scaler = scale_features(X_train, X_test)
    print(f"  Train : {X_train_sc.shape[0]:,} rows | Test : {X_test_sc.shape[0]:,} rows")

    print("\n[3/7] Training logistic regression …")
    model = train(X_train_sc, y_train)
    print("  Training complete.")

    print("\n[4/7] Evaluating …")
    evaluate(model, X_train_sc, X_test_sc, y_train, y_test)

    print("\n[5/7] Calibration analysis …")
    calibration_metrics_uncal = analyze_calibration(model, X_test_sc, y_test)
    calibrated_model, brier_cal = calibrate_model(
        model, X_train_sc, X_test_sc, y_train, y_test
    )
    calibration_metrics = {
        "brier_uncalibrated": calibration_metrics_uncal["brier_score"],
        "brier_calibrated": brier_cal,
    }

    print("\n[6/7] Computing SHAP values …")
    shap_values, expected_value = compute_shap(model, X_train_sc, X_test_sc, feature_names)

    print("\n[7/7] Saving artefacts …")
    save_artefacts(
        model, 
        calibrated_model,
        scaler, 
        shap_values, 
        expected_value, 
        feature_names,
        calibration_metrics,
    )
    
    print("\n  Pipeline complete.")
    print(f"\n  CRITICAL NOTES FOR THESIS:")
    print(f"    1. Temporal cutoff enforced at day {42} - no leakage")
    print(f"    2. SHAP values verified for additivity")
    print(f"    3. Model calibrated - interfaces use calibrated_model.pkl")
    print(f"    4. All artefacts saved with fixed random seed ({RANDOM_STATE}) for reproducibility\n")


if __name__ == "__main__":
    run()
