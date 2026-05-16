"""
SHAP Explainer Layer
─────────────────────────────────────────────────────────────────────────────
Loads saved model artefacts and produces per-instance SHAP explanations.
Consumed by both interface variants; Variant A ignores shap_values in the UI.
─────────────────────────────────────────────────────────────────────────────
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

import joblib
import shap

SAVE_DIR = Path("models/saved_models")


def load_artefacts() -> tuple:
    """Load model, scaler, and feature names from saved_models/."""
    model = joblib.load(SAVE_DIR / "logistic_regression.pkl")
    scaler = joblib.load(SAVE_DIR / "scaler.pkl")
    with open(SAVE_DIR / "feature_names.json") as f:
        feature_names = json.load(f)
    return model, scaler, feature_names


def explain(
    student_row: pd.DataFrame,
    model,
    scaler,
    feature_names: list[str],
) -> dict:
    """
    Produce a full explanation for a single student row.

    Parameters
    ----------
    student_row : DataFrame with exactly one row, columns matching feature_names

    Returns
    -------
    dict with:
      prediction     — 0 (At-Risk) or 1 (Success)
      probability    — P(Success) as float
      label          — human-readable string
      shap_values    — dict {feature: shap_value}
      expected_value — model base value (log-odds intercept)
      feature_names  — ordered list (for consistent chart rendering)
    """
    row_sc = scaler.transform(student_row[feature_names])

    prediction = int(model.predict(row_sc)[0])
    probability = float(model.predict_proba(row_sc)[0][1])
    label = "At-Risk" if prediction == 0 else "Success"

    # Background = zero vector, which equals the training-data mean after
    # StandardScaler. This compares the student against the average student
    # rather than against themselves, producing meaningful non-zero SHAP values.
    background = np.zeros((1, row_sc.shape[1]))
    explainer = shap.LinearExplainer(
        model, background, feature_perturbation="interventional"
    )
    sv = explainer.shap_values(row_sc)[0]

    return {
        "prediction": prediction,
        "probability": probability,
        "label": label,
        "shap_values": dict(zip(feature_names, sv.tolist())),
        "expected_value": float(explainer.expected_value),
        "feature_names": feature_names,
    }
