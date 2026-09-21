"""
Variant A — Control Interface (Prediction Only)
─────────────────────────────────────────────────────────────────────────────
Shows the student risk prediction label and probability.
No SHAP explanation is shown — this is the control condition.
─────────────────────────────────────────────────────────────────────────────
Run:  streamlit run interfaces/variant_a_static/app.py
"""

import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from xai.shap_explainer import load_artefacts, explain
from interfaces.shared_components.student_form import render_form, encode_input

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Risk Prediction",
    page_icon="🎓",
    layout="centered",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F7FAFC; }
    .risk-box {
        border-radius: 12px;
        padding: 28px 32px;
        text-align: center;
        margin-top: 24px;
    }
    .at-risk {
        background-color: #FFF5F5;
        border: 2px solid #FC8181;
    }
    .success {
        background-color: #F0FFF4;
        border: 2px solid #68D391;
    }
    .risk-label {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .risk-prob {
        font-size: 1rem;
        color: #718096;
    }
    .divider { margin: 24px 0; border-top: 1px solid #E2E8F0; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("Student Risk Prediction")
st.caption("Educational Decision-Support System  ·  Variant A")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Load model artefacts (cached) ──────────────────────────────────────────────
@st.cache_resource
def get_artefacts():
    return load_artefacts()

model, scaler, feature_names = get_artefacts()

# ── Input form ─────────────────────────────────────────────────────────────────
raw = render_form()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Predict ────────────────────────────────────────────────────────────────────
if st.button("Predict Risk", type="primary", use_container_width=True):
    student_df = encode_input(raw, feature_names)
    result = explain(student_df, model, scaler, feature_names)

    label = result["label"]
    prob = result["probability"]
    is_at_risk = result["prediction"] == 0

    box_class = "at-risk" if is_at_risk else "success"
    emoji = "⚠" if is_at_risk else "☑️"
    color = "#C53030" if is_at_risk else "#276749"
    prob_display = (1 - prob) if is_at_risk else prob

    st.markdown(f"""
    <div class="risk-box {box_class}">
        <div class="risk-label" style="color:{color};">{emoji} Predicted: {label}</div>
        <div class="risk-prob">Confidence: {prob_display:.1%}</div>
    </div>
    """, unsafe_allow_html=True)
