"""
Variant B — Experimental Interface (Explainable + Progressive Disclosure)
─────────────────────────────────────────────────────────────────────────────
Three-layer progressive disclosure:
  Layer 1 (always visible)  — Prediction summary (label + confidence)
  Layer 2 (expander 1)      — Human-readable, non-technical explanation
  Layer 3 (expander 2)      — Technical SHAP charts and contribution table
─────────────────────────────────────────────────────────────────────────────
Run:  streamlit run interfaces/variant_b_progressive/app.py
"""

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from xai.shap_explainer import load_artefacts, explain
from xai.explainer_utils import shap_bar_chart, shap_waterfall_chart
from interfaces.shared_components.student_form import render_form, encode_input


# ── Natural-language explanation generator ─────────────────────────────────────
#
# Each feature has two sentence templates:
#   "support"  — SHAP > 0, feature pushed the prediction toward Success
#   "concern"  — SHAP < 0, feature pushed the prediction toward At-Risk
#
# Templates use plain English so any educator or adviser can read them without
# ML background. No SHAP values, coefficients, or log-odds are mentioned.

_TEMPLATES: dict[str, dict[str, str]] = {
    "avg_assessment_score": {
        "support": "High assessment scores positively influenced the prediction, reflecting strong academic performance.",
        "concern": "Below-average assessment scores contributed negatively to the prediction, indicating academic difficulty.",
    },
    "total_clicks": {
        "support": "Frequent interaction with the learning platform supported the prediction, showing active online engagement.",
        "concern": "Low engagement with the learning platform contributed negatively, suggesting limited use of online resources.",
    },
    "num_activities_accessed": {
        "support": "Accessing a wide range of course materials indicated strong participation and contributed positively.",
        "concern": "Limited activity access indicated reduced participation in course content, contributing to the at-risk signal.",
    },
    "num_assessments_completed": {
        "support": "Completing multiple assessments demonstrated consistent academic effort and supported the prediction.",
        "concern": "Fewer completed assessments were noted, suggesting inconsistent engagement with coursework.",
    },
    "studied_credits": {
        "support": "The student's credit load was within a range associated with manageable academic progress.",
        "concern": "A high credit load may reflect increased academic pressure, which contributed to the prediction.",
    },
    "gender_M": {
        "support": "Gender was a minor factor that slightly supported the prediction outcome.",
        "concern": "Gender was identified as a minor contributing factor to the prediction.",
    },
    "disability_Y": {
        "support": "Disability status was considered and showed a small positive association with the outcome.",
        "concern": "Disability status was identified as a minor contributing factor. Additional support may be beneficial.",
    },
    "age_band_35-55": {
        "support": "The student's age group showed a positive association with the predicted outcome.",
        "concern": "The student's age group was noted as a minor contributing factor to the prediction.",
    },
    "age_band_55<=": {
        "support": "The student's age group showed a positive association with the predicted outcome.",
        "concern": "The student's age group was noted as a minor contributing factor to the prediction.",
    },
}

# Shared template for all highest_education one-hot columns
_EDUCATION_TEMPLATE = {
    "support": "The student's educational background was a positive factor in the prediction.",
    "concern": "The student's prior educational attainment was noted as a contributing factor to the prediction.",
}

_EDUCATION_FEATURES = [
    "highest_education_HE Qualification",
    "highest_education_Lower Than A Level",
    "highest_education_No Formal quals",
    "highest_education_Post Graduate Qualification",
]
for _ef in _EDUCATION_FEATURES:
    _TEMPLATES[_ef] = _EDUCATION_TEMPLATE


def generate_explanation(shap_values: dict[str, float], top_n: int = 5) -> list[str]:
    """
    Convert top SHAP contributors into human-readable bullet sentences.

    Logic:
      - Sort features by absolute SHAP value (largest impact first).
      - For each top feature, choose the 'support' or 'concern' template
        based on whether SHAP > 0 (pushes toward Success) or < 0 (At-Risk).
      - Skip features with negligible impact (|SHAP| < 0.005).
    """
    sorted_items = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)

    sentences = []
    for feature, value in sorted_items[:top_n]:
        if abs(value) < 0.005:
            continue
        direction = "support" if value > 0 else "concern"
        template = _TEMPLATES.get(feature)
        if template:
            sentences.append((direction, template[direction]))

    return sentences


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Explainable Student Risk Prediction",
    page_icon="🎓",
    layout="wide",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F7FAFC; }

    .risk-box {
        border-radius: 12px;
        padding: 24px 28px;
        text-align: center;
        margin-top: 12px;
        margin-bottom: 20px;
    }
    .at-risk  { background-color: #FFF5F5; border: 2px solid #FC8181; }
    .success  { background-color: #F0FFF4; border: 2px solid #68D391; }
    .risk-label { font-size: 1.8rem; font-weight: 700; margin-bottom: 6px; }
    .risk-prob  { font-size: 0.95rem; color: #718096; }

    .nl-support {
        background: #F0FFF4;
        border-left: 4px solid #68D391;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.92rem;
        color: #22543D;
    }
    .nl-concern {
        background: #FFF5F5;
        border-left: 4px solid #FC8181;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.92rem;
        color: #742A2A;
    }

    .legend-row { display: flex; gap: 20px; margin-bottom: 10px; font-size: 0.85rem; color: #4A5568; }
    .legend-dot { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 5px; }
    .divider { margin: 20px 0; border-top: 1px solid #E2E8F0; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("Explainable Student Risk Prediction")
st.caption("Educational Decision-Support System  ·  Variant B  ·  Powered by SHAP")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Load artefacts (cached across reruns) ──────────────────────────────────────
@st.cache_resource
def get_artefacts():
    return load_artefacts()

model, scaler, feature_names = get_artefacts()

# ── Layout ─────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1.4], gap="large")

with left_col:
    raw = render_form()
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    predict_clicked = st.button("Predict & Explain", type="primary", use_container_width=True)

with right_col:
    if not predict_clicked:
        st.info("Fill in the student profile on the left and click **Predict & Explain**.")

    else:
        student_df = encode_input(raw, feature_names)
        result = explain(student_df, model, scaler, feature_names)

        label        = result["label"]
        prob         = result["probability"]
        shap_values  = result["shap_values"]
        expected_val = result["expected_value"]
        is_at_risk   = result["prediction"] == 0

        box_class    = "at-risk" if is_at_risk else "success"
        emoji        = "⚠️" if is_at_risk else "✅"
        color        = "#C53030" if is_at_risk else "#276749"
        prob_display = (1 - prob) if is_at_risk else prob

        # ── LAYER 1: Prediction summary (always visible) ───────────────────────
        st.markdown(f"""
        <div class="risk-box {box_class}">
            <div class="risk-label" style="color:{color};">{emoji} Predicted: {label}</div>
            <div class="risk-prob">Prediction confidence: {prob_display:.1%}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── LAYER 2: Human-readable explanation (expander 1) ──────────────────
        with st.expander("Why was this prediction made?", expanded=True):
            st.markdown(
                "The following factors had the greatest influence on this student's prediction. "
                "Factors highlighted in **green** supported a positive outcome, while those in "
                "**red** raised concern."
            )
            st.markdown("")

            sentences = generate_explanation(shap_values, top_n=5)

            if sentences:
                for direction, text in sentences:
                    css_class = "nl-support" if direction == "support" else "nl-concern"
                    icon = "✔" if direction == "support" else "✖"
                    st.markdown(
                        f'<div class="{css_class}">{icon}&nbsp; {text}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown("_No dominant factors identified for this prediction._")

        # ── LAYER 3: Technical SHAP details (expander 2) ──────────────────────
        with st.expander("Show Detailed Technical Explanation"):
            st.markdown(
                "The charts below show the precise contribution of each feature to this "
                "prediction, measured using SHAP (SHapley Additive exPlanations). "
                "Features pushing the model toward **At-Risk** appear in red; "
                "those pushing toward **Success** appear in green."
            )

            st.markdown("")
            st.markdown("""
            <div class="legend-row">
                <span><span class="legend-dot" style="background:#FC8181;"></span>Increases At-Risk probability</span>
                <span><span class="legend-dot" style="background:#68D391;"></span>Reduces At-Risk probability</span>
            </div>
            """, unsafe_allow_html=True)

            # SHAP bar chart
            fig_bar = shap_bar_chart(
                shap_values, top_n=10, title="Feature Impact on Prediction (SHAP)"
            )
            st.pyplot(fig_bar, use_container_width=True)

            st.markdown("")

            # Waterfall chart
            st.markdown("**How features shift the prediction from the baseline average:**")
            fig_wf = shap_waterfall_chart(
                shap_values,
                expected_value=expected_val,
                prediction_value=prob,
                top_n=8,
            )
            st.pyplot(fig_wf, use_container_width=True)

            # Contribution table
            st.markdown("**Full feature contribution table:**")
            contrib_df = (
                pd.DataFrame(list(shap_values.items()), columns=["Feature", "SHAP Value"])
                .assign(Direction=lambda d: d["SHAP Value"].apply(
                    lambda v: "↑ Increases At-Risk" if v < 0 else "↓ Reduces At-Risk"
                ))
                .sort_values("SHAP Value", key=abs, ascending=False)
                .reset_index(drop=True)
            )
            contrib_df["SHAP Value"] = contrib_df["SHAP Value"].map("{:+.4f}".format)
            st.dataframe(contrib_df, use_container_width=True, hide_index=True)
