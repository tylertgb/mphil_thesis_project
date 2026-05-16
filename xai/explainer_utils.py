"""
SHAP Visualisation Utilities
─────────────────────────────────────────────────────────────────────────────
Generates matplotlib figures for the Variant B progressive disclosure panel.
─────────────────────────────────────────────────────────────────────────────
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for Streamlit
import matplotlib.pyplot as plt


# Colour palette consistent with the interface design
AT_RISK_COLOR = "#E53E3E"
SUCCESS_COLOR = "#38A169"
POSITIVE_SHAP = "#FC8181"   # pushes toward At-Risk
NEGATIVE_SHAP = "#68D391"   # pushes toward Success
NEUTRAL_COLOR = "#CBD5E0"


def shap_bar_chart(
    shap_values: dict[str, float],
    top_n: int = 10,
    title: str = "Top Feature Contributions",
) -> plt.Figure:
    """
    Horizontal bar chart of the top-N features by |SHAP value|.
    Positive bars (red) push the prediction toward At-Risk.
    Negative bars (green) push toward Success.
    """
    sorted_items = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
    items = sorted_items[:top_n]

    features = [_clean_label(k) for k, _ in items]
    values = [v for _, v in items]
    colors = [POSITIVE_SHAP if v > 0 else NEGATIVE_SHAP for v in values]

    fig, ax = plt.subplots(figsize=(7, max(3, len(features) * 0.45)))
    bars = ax.barh(features[::-1], values[::-1], color=colors[::-1], edgecolor="white", height=0.6)

    ax.axvline(0, color="#4A5568", linewidth=0.8, linestyle="--")
    ax.set_xlabel("SHAP Value  (impact on prediction)", fontsize=9, color="#4A5568")
    ax.set_title(title, fontsize=11, fontweight="bold", color="#2D3748", pad=10)
    ax.tick_params(axis="y", labelsize=8.5, colors="#4A5568")
    ax.tick_params(axis="x", labelsize=8, colors="#4A5568")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#CBD5E0")

    # Value labels on bars
    for bar, val in zip(bars[::-1], values[::-1]):
        ax.text(
            val + (0.002 if val >= 0 else -0.002),
            bar.get_y() + bar.get_height() / 2,
            f"{val:+.3f}",
            va="center",
            ha="left" if val >= 0 else "right",
            fontsize=7.5,
            color="#2D3748",
        )

    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")
    plt.tight_layout()
    return fig


def shap_waterfall_chart(
    shap_values: dict[str, float],
    expected_value: float,
    prediction_value: float,
    top_n: int = 8,
) -> plt.Figure:
    """
    Simplified waterfall chart showing how each feature shifts the
    prediction away from the base (expected) value.
    """
    sorted_items = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
    items = sorted_items[:top_n]

    features = [_clean_label(k) for k, _ in items]
    values = [v for _, v in items]

    cumulative = expected_value
    starts, widths, colors = [], [], []
    for v in values:
        starts.append(cumulative)
        widths.append(v)
        colors.append(POSITIVE_SHAP if v > 0 else NEGATIVE_SHAP)
        cumulative += v

    fig, ax = plt.subplots(figsize=(7, max(3.5, len(features) * 0.5 + 1.2)))
    y_pos = list(range(len(features)))

    ax.barh(y_pos, widths, left=starts, color=colors, edgecolor="white", height=0.55)
    ax.axvline(expected_value, color="#718096", linewidth=1, linestyle=":", label=f"Base: {expected_value:.3f}")
    ax.axvline(prediction_value, color="#2D3748", linewidth=1.2, linestyle="--", label=f"Prediction: {prediction_value:.3f}")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(features, fontsize=8.5)
    ax.set_xlabel("Model output (log-odds contribution)", fontsize=9, color="#4A5568")
    ax.set_title("How features shift the prediction from baseline", fontsize=11, fontweight="bold", color="#2D3748", pad=10)
    ax.legend(fontsize=8, framealpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#CBD5E0")
    ax.tick_params(colors="#4A5568")

    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")
    plt.tight_layout()
    return fig


def _clean_label(feature_name: str) -> str:
    """Convert one-hot encoded column names to readable labels."""
    replacements = {
        "gender_M": "Gender: Male",
        "disability_Y": "Has Disability",
        "age_band_35-55": "Age: 35–55",
        "age_band_55<=": "Age: 55+",
        "highest_education_HE Qualification": "Education: HE Qualification",
        "highest_education_Lower Than A Level": "Education: Below A-Level",
        "highest_education_No Formal quals": "Education: No Formal Quals",
        "highest_education_Post Graduate Qualification": "Education: Postgraduate",
        "studied_credits": "Credits Studied",
        "avg_assessment_score": "Avg. Assessment Score",
        "num_assessments_completed": "Assessments Completed",
        "total_clicks": "Total VLE Clicks",
        "num_activities_accessed": "Activities Accessed",
    }
    return replacements.get(feature_name, feature_name.replace("_", " ").title())
