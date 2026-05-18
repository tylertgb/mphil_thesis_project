"""
Model Evaluation — Chapter 4: Preliminary Model Performance Metrics
─────────────────────────────────────────────────────────────────────────────
MPhil Thesis: A Human-Centered Evaluation of SHAP-Based Explainable Interfaces
              for Logistic Regression Models in Educational Decision-Support Systems

Evaluates the trained Logistic Regression model on the held-out test set and
produces Table 4.2 (model performance metrics) and the confusion matrix figure.

Usage:
    python evaluation.py

Output:
    Console  — metrics table, classification report, confusion matrix values
    results/figures/confusion_matrix.png — publication-ready confusion matrix
─────────────────────────────────────────────────────────────────────────────
"""

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

# ── Paths (mirror constants from logistic_regression_model.py) ─────────────────
DATA_FILE  = Path("data/processed/final_model_dataset.csv")
SAVE_DIR   = Path("models/saved_models")
FIG_DIR    = Path("results/figures")

# Must match training configuration exactly to reproduce the same test split
TEST_SIZE    = 0.2
RANDOM_STATE = 42

CLASS_NAMES  = ["At-Risk (0)", "Success (1)"]


# ── Step 1: Load saved artefacts ───────────────────────────────────────────────

def load_artefacts():
    """Load the trained model, scaler, and feature names from saved_models/."""
    model  = joblib.load(SAVE_DIR / "logistic_regression.pkl")
    scaler = joblib.load(SAVE_DIR / "scaler.pkl")
    with open(SAVE_DIR / "feature_names.json") as f:
        feature_names = json.load(f)
    return model, scaler, feature_names


# ── Step 2: Reconstruct the test split ────────────────────────────────────────

def get_test_split(feature_names: list[str]):
    """
    Reload the processed dataset and reproduce the identical test split used
    during training (same TEST_SIZE and RANDOM_STATE).
    Returns scaled X_test and y_test.
    """
    df = pd.read_csv(DATA_FILE)
    X  = df.drop(columns=["target"])
    y  = df["target"]

    # Impute any residual NaNs from left-joins (mirrors logistic_regression_model.py)
    for col in X.columns:
        if X[col].isnull().any():
            X[col] = X[col].fillna(X[col].median())

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    return X_test[feature_names], y_test


# ── Step 3: Compute metrics ────────────────────────────────────────────────────

def compute_metrics(model, scaler, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """
    Scale the test features and compute core classification metrics.
    All values rounded to 2 decimal places for thesis reporting.
    """
    X_test_sc = scaler.transform(X_test)
    y_pred    = model.predict(X_test_sc)

    metrics = {
        "Accuracy":  round(accuracy_score(y_test, y_pred), 2),
        "Precision": round(precision_score(y_test, y_pred, average="weighted"), 2),
        "Recall":    round(recall_score(y_test, y_pred, average="weighted"), 2),
        "F1-Score":  round(f1_score(y_test, y_pred, average="weighted"), 2),
    }
    return metrics, X_test_sc, y_pred


# ── Step 4: Print classification report ───────────────────────────────────────

def print_classification_report(y_test: pd.Series, y_pred: np.ndarray) -> None:
    """Print the full per-class classification report."""
    divider = "─" * 58
    print(f"\n{divider}")
    print("  Classification Report")
    print(divider)
    print(classification_report(y_test, y_pred, target_names=CLASS_NAMES, digits=2))


# ── Step 5: Build Table 4.2 ───────────────────────────────────────────────────

def build_metrics_table(metrics: dict) -> pd.DataFrame:
    """
    Construct a clean DataFrame for Table 4.2:
    'Preliminary Model Performance Metrics' in the thesis.
    """
    table = pd.DataFrame(
        {"Metric": list(metrics.keys()), "Value": list(metrics.values())}
    )
    return table


# ── Step 6: Confusion matrix figure ───────────────────────────────────────────

def save_confusion_matrix(y_test: pd.Series, y_pred: np.ndarray) -> None:
    """
    Generate and save a publication-ready confusion matrix heatmap.
    Saved to results/figures/confusion_matrix.png.
    """
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(6, 5))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=CLASS_NAMES,
        yticklabels=CLASS_NAMES,
        linewidths=0.5,
        linecolor="#E2E8F0",
        ax=ax,
        annot_kws={"size": 13, "weight": "bold"},
    )

    ax.set_xlabel("Predicted Label", fontsize=11, labelpad=10)
    ax.set_ylabel("True Label", fontsize=11, labelpad=10)
    ax.set_title(
        "Figure 4.1: Confusion Matrix — Logistic Regression\n"
        "(OULAD Test Set)",
        fontsize=11,
        fontweight="bold",
        pad=14,
        color="#2D3748",
    )

    # Annotate TN / FP / FN / TP quadrants
    labels = [["TN", "FP"], ["FN", "TP"]]
    for i in range(2):
        for j in range(2):
            ax.text(
                j + 0.5, i + 0.78,
                labels[i][j],
                ha="center", va="center",
                fontsize=8, color="#718096",
            )

    plt.tight_layout()
    output_path = FIG_DIR / "confusion_matrix.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  Confusion matrix saved → {output_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

def run() -> None:
    divider = "─" * 58

    # Load
    print(f"\n{divider}")
    print("  Loading model artefacts …")
    print(divider)
    model, scaler, feature_names = load_artefacts()
    print(f"  Model    : {type(model).__name__}")
    print(f"  Features : {len(feature_names)}")

    # Reconstruct test split
    print(f"\n  Reconstructing test split (size={TEST_SIZE}, seed={RANDOM_STATE}) …")
    X_test, y_test = get_test_split(feature_names)
    print(f"  Test set : {X_test.shape[0]:,} rows")

    # Compute metrics
    metrics, X_test_sc, y_pred = compute_metrics(model, scaler, X_test, y_test)

    # ── Table 4.2 ──────────────────────────────────────────────────────────────
    print(f"\n{divider}")
    print("  Table 4.2: Preliminary Model Performance Metrics")
    print(divider)
    table = build_metrics_table(metrics)
    print(table.to_string(index=False))
    print(divider)

    # ── Classification report ──────────────────────────────────────────────────
    print_classification_report(y_test, y_pred)

    # ── Confusion matrix values ────────────────────────────────────────────────
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n{divider}")
    print("  Confusion Matrix")
    print(divider)
    print(f"  {'':20} Predicted At-Risk   Predicted Success")
    print(f"  {'Actual At-Risk':<20} TN = {cm[0,0]:>6,}         FP = {cm[0,1]:>6,}")
    print(f"  {'Actual Success':<20} FN = {cm[1,0]:>6,}         TP = {cm[1,1]:>6,}")
    print(divider)

    # ── Save figure ────────────────────────────────────────────────────────────
    save_confusion_matrix(y_test, y_pred)

    print(f"\n  Evaluation complete.\n")

    return table


if __name__ == "__main__":
    run()
