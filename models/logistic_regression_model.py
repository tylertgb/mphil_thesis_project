"""
Logistic Regression Model + SHAP Explainer
─────────────────────────────────────────────────────────────────────────────
MPhil Thesis: A Human-Centered Evaluation of SHAP-Based Explainable Interfaces
              for Logistic Regression Models in Educational Decision-Support Systems

Input  : data/processed/final_model_dataset.csv
Output : models/saved_models/logistic_regression.pkl
         models/saved_models/scaler.pkl
         models/saved_models/shap_values.npy
         models/saved_models/shap_expected_value.npy
         models/saved_models/feature_names.json
─────────────────────────────────────────────────────────────────────────────
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
import joblib
import shap

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_FILE = Path("data/processed/final_model_dataset.csv")
SAVE_DIR = Path("models/saved_models")

# ── Hyperparameters ────────────────────────────────────────────────────────────
TEST_SIZE = 0.2
RANDOM_STATE = 42
CV_FOLDS = 5


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

    divider = "─" * 54
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


# ── 5. SHAP explanation ────────────────────────────────────────────────────────


def compute_shap(
    model: LogisticRegression,
    X_train: np.ndarray,
    X_test: np.ndarray,
    feature_names: list[str],
) -> tuple[np.ndarray, float]:
    """
    Compute SHAP values using LinearExplainer (exact for linear models).
    Returns SHAP values for the test set and the model's expected value.
    SHAP values are computed for class 1 (Success / At-Risk probability).
    """
    explainer = shap.LinearExplainer(model, X_train, feature_perturbation="interventional")
    shap_values = explainer.shap_values(X_test)

    print("\n  SHAP Summary (mean |SHAP| per feature — top 10):")
    mean_abs = np.abs(shap_values).mean(axis=0)
    ranking = np.argsort(mean_abs)[::-1]
    for rank, idx in enumerate(ranking[:10], 1):
        print(f"    {rank:>2}. {feature_names[idx]:<40} {mean_abs[idx]:.4f}")

    return shap_values, explainer.expected_value


# ── 6. Persistence ─────────────────────────────────────────────────────────────


def save_artefacts(
    model: LogisticRegression,
    scaler: StandardScaler,
    shap_values: np.ndarray,
    expected_value: float,
    feature_names: list[str],
) -> None:
    """Serialise all artefacts consumed by the interface variants and notebooks."""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, SAVE_DIR / "logistic_regression.pkl")
    joblib.dump(scaler, SAVE_DIR / "scaler.pkl")
    np.save(SAVE_DIR / "shap_values.npy", shap_values)
    np.save(SAVE_DIR / "shap_expected_value.npy", np.array([expected_value]))

    with open(SAVE_DIR / "feature_names.json", "w") as f:
        json.dump(feature_names, f, indent=2)

    print(f"\n  Artefacts saved to {SAVE_DIR}/")
    for p in sorted(SAVE_DIR.iterdir()):
        print(f"    {p.name}")


# ── 7. Inference helper (used by both interface variants) ──────────────────────


def predict_student(
    student_features: dict,
    model: LogisticRegression | None = None,
    scaler: StandardScaler | None = None,
    feature_names: list[str] | None = None,
) -> dict:
    """
    Run inference for a single student record.

    Parameters
    ----------
    student_features : dict mapping feature name → raw value
    model, scaler, feature_names : loaded from saved_models/ if not supplied

    Returns
    -------
    dict with keys:
      prediction    — 0 (At-Risk) or 1 (Success)
      probability   — P(Success)
      label         — human-readable string
      shap_values   — per-feature SHAP contributions (used by Variant B)
    """
    if model is None:
        model = joblib.load(SAVE_DIR / "logistic_regression.pkl")
    if scaler is None:
        scaler = joblib.load(SAVE_DIR / "scaler.pkl")
    if feature_names is None:
        with open(SAVE_DIR / "feature_names.json") as f:
            feature_names = json.load(f)

    row = pd.DataFrame([student_features])[feature_names]
    row_sc = scaler.transform(row)

    prediction = int(model.predict(row_sc)[0])
    probability = float(model.predict_proba(row_sc)[0][1])
    label = "Success" if prediction == 1 else "At-Risk"

    # Per-instance SHAP for Variant B interface
    explainer = shap.LinearExplainer(model, row_sc, feature_perturbation="interventional")
    instance_shap = explainer.shap_values(row_sc)[0]

    return {
        "prediction": prediction,
        "probability": round(probability, 4),
        "label": label,
        "shap_values": dict(zip(feature_names, instance_shap.tolist())),
    }


# ── Main ───────────────────────────────────────────────────────────────────────


def run() -> None:
    print("\n[1/5] Loading data …")
    X, y = load_data()
    X = impute_remaining(X)
    feature_names = X.columns.tolist()

    print("\n[2/5] Splitting and scaling …")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    X_train_sc, X_test_sc, scaler = scale_features(X_train, X_test)
    print(f"  Train : {X_train_sc.shape[0]:,} rows | Test : {X_test_sc.shape[0]:,} rows")

    print("\n[3/5] Training logistic regression …")
    model = train(X_train_sc, y_train)
    print("  Training complete.")

    print("\n[4/5] Evaluating …")
    evaluate(model, X_train_sc, X_test_sc, y_train, y_test)

    print("\n[5/5] Computing SHAP values …")
    shap_values, expected_value = compute_shap(model, X_train_sc, X_test_sc, feature_names)

    save_artefacts(model, scaler, shap_values, expected_value, feature_names)
    print("\n  Pipeline complete.\n")


if __name__ == "__main__":
    run()
