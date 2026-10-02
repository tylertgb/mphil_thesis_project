"""
Variant B — Experimental Interface with Integrated Study Questionnaires
─────────────────────────────────────────────────────────────────────────────
Multi-page study flow with progressive SHAP explanations:
  1. Task Case 1 → Prediction + SHAP Explanation → Decision Confidence
  2. Task Case 2 → Prediction + SHAP Explanation → Decision Confidence
  3. Task Case 3 → Prediction + SHAP Explanation → Decision Confidence
  4. SUS + Trust + Understanding questionnaires
  5. Thank you

Three-layer progressive disclosure:
  Layer 1 (always visible)  — Prediction summary (label + confidence)
  Layer 2 (expander 1)      — Human-readable, non-technical explanation
  Layer 3 (expander 2)      — Technical SHAP charts and contribution table
─────────────────────────────────────────────────────────────────────────────
Deployed URL: https://mphil-study-variant-b.streamlit.app
"""

import sys
import pandas as pd
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from xai.shap_explainer import load_artefacts, explain
from xai.explainer_utils import shap_bar_chart, shap_waterfall_chart
from interfaces.shared_components.participant_session import (
    initialize_session, mark_task_completed, get_study_progress, save_session_to_file
)
from interfaces.shared_components.questionnaire_forms import (
    render_sus_form, render_trust_form,
    render_understanding_form, render_decision_confidence_form
)
from utils.dual_logger import DualLogger


# ── Natural-language explanation generator (same as original) ──────────────────
_TEMPLATES: dict[str, dict[str, str]] = {
    "avg_assessment_score": {
        "support": "High assessment scores positively influenced the prediction, reflecting strong academic performance.",
        "concern": "Below-average assessment scores contributed negatively to the prediction, indicating academic difficulty.",
    },
    "total_clicks_pre_cutoff": {
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
    "days_active": {
        "support": "Consistent online presence over time supported the prediction, indicating sustained engagement.",
        "concern": "Limited days of activity suggested irregular engagement patterns.",
    },
    "completion_rate": {
        "support": "High assessment completion rate demonstrated academic commitment.",
        "concern": "Lower completion rate indicated potential engagement challenges.",
    },
}


def generate_explanation(shap_values: dict[str, float], top_n: int = 5) -> list[tuple[str, str]]:
    """Convert top SHAP contributors into human-readable bullet sentences."""
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
    page_title="Explainable Student Risk Prediction - Variant B",
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
    .progress-bar {
        background: #E2E8F0;
        border-radius: 8px;
        height: 8px;
        margin: 16px 0;
    }
    .progress-fill {
        background: #4299E1;
        height: 100%;
        border-radius: 8px;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# ── Initialize session ─────────────────────────────────────────────────────────
initialize_session()

# ── Load task cases ────────────────────────────────────────────────────────────
@st.cache_data
def load_task_cases():
    """Load pre-defined task cases from JSON."""
    cases_file = Path(__file__).resolve().parents[2] / "study_task_cases.json"
    with open(cases_file, 'r') as f:
        data = json.load(f)
    return data['cases']

TASK_CASES = load_task_cases()

# Define task assignment (3 cases for Variant B - different from Variant A)
VARIANT_B_TASKS = ["high_risk_2", "medium_risk_5", "low_risk_8"]

# ── Load artefacts (cached) ────────────────────────────────────────────────────
@st.cache_resource
def get_artefacts():
    return load_artefacts()

model, scaler, feature_names = get_artefacts()

# ── Initialize logger ──────────────────────────────────────────────────────────
logger = DualLogger(output_dir="study_data")

# ── Study Flow State Machine ───────────────────────────────────────────────────

# Check if participant ID exists - manual entry if not
if st.session_state.participant_id is None:
    st.warning("⚠️ **No active session found**")
    st.info("Please enter your Participant ID from Variant A to continue.")
    
    with st.form("participant_id_form"):
        st.markdown("### Enter Your Participant ID")
        st.caption("Your Participant ID was shown at the end of Variant A (e.g., P001, P002, etc.)")
        
        participant_id_input = st.text_input(
            "Participant ID",
            placeholder="P001",
            help="Enter the ID you received after completing Variant A"
        ).strip().upper()
        
        submit_btn = st.form_submit_button("Continue to Variant B", type="primary", use_container_width=True)
        
        if submit_btn:
            if participant_id_input and participant_id_input.startswith("P"):
                st.session_state.participant_id = participant_id_input
                st.session_state.demographics_completed = True
                st.success(f"✅ Welcome back, {participant_id_input}!")
                st.rerun()
            else:
                st.error("Please enter a valid Participant ID (e.g., P001)")
    
    st.stop()

# Reset variant B tracking if needed
if 'current_task_index_b' not in st.session_state:
    st.session_state.current_task_index_b = 0
if 'variant_b_completed' not in st.session_state:
    st.session_state.variant_b_completed = False

# Show progress
st.caption(f"Participant ID: {st.session_state.participant_id} | Variant B (Progressive)")

# ── Phase 1: Task Cases ────────────────────────────────────────────────────────

current_task_idx = st.session_state.current_task_index_b

if current_task_idx < len(VARIANT_B_TASKS):
    task_id = VARIANT_B_TASKS[current_task_idx]
    task_case = next(case for case in TASK_CASES if case['case_id'] == task_id)
    
    # Show progress bar
    progress_pct = (current_task_idx / len(VARIANT_B_TASKS)) * 100
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress_pct}%"></div>
    </div>
    <p style="text-align:center; color:#718096; font-size:0.9rem;">
        Task {current_task_idx + 1} of {len(VARIANT_B_TASKS)}: {task_case['risk_category']}
    </p>
    """, unsafe_allow_html=True)
    
    st.title("Explainable Student Risk Prediction")
    st.caption("Educational Decision-Support System  ·  Variant B  ·  Powered by SHAP")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Initialize state flags
    if f"prediction_shown_b_{task_id}" not in st.session_state:
        st.session_state[f"prediction_shown_b_{task_id}"] = False
    if f"ready_for_confidence_b_{task_id}" not in st.session_state:
        st.session_state[f"ready_for_confidence_b_{task_id}"] = False
    
    # State 1: Show profile + "Get Prediction" button
    if not st.session_state[f"prediction_shown_b_{task_id}"]:
        left_col, right_col = st.columns([1, 1.4], gap="large")
        
        with left_col:
            st.info(f"**Scenario:** Review the student profile and prediction.")
            
            # Pre-fill form with task case data
            features = task_case['features']
            
            with st.expander("📊 Student Profile", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Credits", f"{features['studied_credits']:.0f}")
                    st.metric("Prev Attempts", f"{features['num_of_prev_attempts']:.0f}")
                    st.metric("Avg Score", f"{features.get('avg_assessment_score', 'N/A')}")
                    st.metric("Completed", f"{features['num_assessments_completed']:.0f}")
                    st.metric("Due", f"{features['num_assessments_due']:.0f}")
                
                with col2:
                    st.metric("Completion", f"{features['completion_rate']:.0%}")
                    st.metric("VLE Clicks", f"{features['total_clicks_pre_cutoff']:.0f}")
                    st.metric("Activities", f"{features['num_activities_accessed']:.0f}")
                    st.metric("Days Active", f"{features['days_active']:.0f}")
                    st.metric("Clicks/Day", f"{features['avg_clicks_per_active_day']:.1f}")
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            # Navigation buttons at bottom
            if current_task_idx > 0:
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("⬅️ Back", use_container_width=True, key=f"back_btn_b_{task_id}_s1"):
                        # Go back to previous task
                        st.session_state.current_task_index_b -= 1
                        prev_task_id = VARIANT_B_TASKS[st.session_state.current_task_index_b]
                        from interfaces.shared_components.participant_session import reset_task_state
                        reset_task_state(prev_task_id)
                        st.rerun()
                with col2:
                    if st.button("Get Prediction", type="primary", use_container_width=True, key=f"get_pred_b_{task_id}"):
                        st.session_state[f"prediction_shown_b_{task_id}"] = True
                        st.rerun()
            else:
                # First task - no back button
                if st.button("Get Prediction & Explanation", type="primary", use_container_width=True, key=f"get_pred_b_{task_id}"):
                    st.session_state[f"prediction_shown_b_{task_id}"] = True
                    st.rerun()
        
        with right_col:
            st.info("Click **Get Prediction & Explanation** to view the result.")
    
    # State 2: Show prediction + explanation + "Continue" button
    elif not st.session_state[f"ready_for_confidence_b_{task_id}"]:
        # Show prediction (using actual task case prediction)
        prob = task_case['probability']
        label = "Success" if task_case['predicted_label'] == 1 else "At-Risk"
        is_at_risk = task_case['predicted_label'] == 0
        
        box_class = "at-risk" if is_at_risk else "success"
        emoji = "⚠️" if is_at_risk else "✅"
        color = "#C53030" if is_at_risk else "#276749"
        prob_display = (1 - prob) if is_at_risk else prob
        
        st.markdown(f"""
        <div class="risk-box {box_class}">
            <div class="risk-label" style="color:{color};">{emoji} Predicted: {label}</div>
            <div class="risk-prob">Prediction confidence: {prob_display:.1%}</div>
        </div>
        """, unsafe_allow_html=True)
        
        shap_values = task_case['shap_values']
        expected_val = task_case['expected_value']
        
        # LAYER 2: Human-readable explanation
        with st.expander("❓ Why was this prediction made?", expanded=True):
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
        
        # LAYER 3: Technical SHAP details
        with st.expander("📊 Show Detailed Technical Explanation"):
            st.markdown(
                "The charts below show the precise contribution of each feature to this "
                "prediction, measured using SHAP (SHapley Additive exPlanations)."
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
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        st.info("📝 **Please review the prediction and explanation above, then click Continue.**")
        
        # Navigation buttons at bottom
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⬅️ Back", use_container_width=True, key=f"back_btn_b_{task_id}_s2"):
                # Go back to profile view
                st.session_state[f"prediction_shown_b_{task_id}"] = False
                st.rerun()
        with col2:
            if st.button("Continue to Questionnaire ➔", type="primary", use_container_width=True, key=f"continue_to_conf_b_{task_id}"):
                st.session_state[f"ready_for_confidence_b_{task_id}"] = True
                st.rerun()
    
    # State 3: Show confidence questionnaire
    else:
        st.info(f"You've reviewed the prediction and explanation. Please complete the questionnaire.")
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        confidence_responses = render_decision_confidence_form(task_id)
        
        # Back button at bottom (before form submission)
        if not confidence_responses:  # Only show if form not submitted
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            if st.button("⬅️ Back", use_container_width=False, key=f"back_btn_b_{task_id}_s3"):
                # Go back to explanation view
                st.session_state[f"ready_for_confidence_b_{task_id}"] = False
                st.rerun()
        
        if confidence_responses:
            # Log decision confidence
            logger.log_decision_confidence(
                st.session_state.participant_id,
                "variant_b",
                task_id,
                confidence_responses
            )
            
            # Mark task as completed
            mark_task_completed(task_id)
            st.session_state.current_task_index_b += 1
            
            st.success(f"✅ Task {current_task_idx + 1} completed!")
            st.rerun()

# ── Phase 2: Post-Variant Questionnaires ───────────────────────────────────────
elif not st.session_state.variant_b_completed:
    st.title("✅ System Evaluation")
    st.markdown("Please complete the following questionnaires about your experience with Variant B.")
    st.markdown("---")
    
    # Check which questionnaires are completed
    if 'sus_completed_b' not in st.session_state:
        st.session_state.sus_completed_b = False
    if 'trust_completed_b' not in st.session_state:
        st.session_state.trust_completed_b = False
    if 'understanding_completed_b' not in st.session_state:
        st.session_state.understanding_completed_b = False
    
    # SUS
    if not st.session_state.sus_completed_b:
        sus_responses = render_sus_form()
        if sus_responses:
            logger.log_sus(st.session_state.participant_id, "variant_b", sus_responses)
            st.session_state.sus_completed_b = True
            st.success("✅ SUS responses saved!")
            st.rerun()
        st.stop()
    
    # Trust
    if not st.session_state.trust_completed_b:
        trust_responses = render_trust_form()
        if trust_responses:
            logger.log_trust(st.session_state.participant_id, "variant_b", trust_responses)
            st.session_state.trust_completed_b = True
            st.success("✅ Trust responses saved!")
            st.rerun()
        st.stop()
    
    # Understanding
    if not st.session_state.understanding_completed_b:
        understanding_responses = render_understanding_form()
        if understanding_responses:
            logger.log_understanding(st.session_state.participant_id, "variant_b", understanding_responses)
            st.session_state.understanding_completed_b = True
            st.session_state.variant_b_completed = True
            
            # Set variant name for session tracking
            st.session_state.variant_name = "variant_b"
            
            # Save session to track completion
            save_session_to_file()
            
            st.success("✅ All responses saved for Variant B!")
            st.rerun()
        st.stop()

# ── Phase 3: Completion ────────────────────────────────────────────────────────
else:
    st.title("✅ Variant B Completed!")
    st.markdown("---")
    
    st.success(f"""
    **🎉 Thank you for completing Variant B!**
    
    You have finished:
    - {len(VARIANT_B_TASKS)} task cases
    - 3 evaluation questionnaires
    """)
    
    st.markdown("### 📋 Final Step: Complete the Comparison Questionnaire")
    st.markdown("Please click the button below to share your overall feedback:")
    
    st.markdown("")  # Spacing
    
    # Red Streamlit-style button that opens in new tab
    st.link_button(
        "📝 Open Final Feedback Form",
        "https://mphil-study-final-feedback.streamlit.app",
        use_container_width=True,
        type="primary"
    )
    
    st.markdown("""
    
    This is the last part of the study where you'll compare both interfaces.
    
    ---
    
    **Alternative: Copy this link if button doesn't work**
    ```
    https://mphil-study-final-feedback.streamlit.app
    ```
    
    ---
    """)
    
    st.success(f"✅ Session saved: {st.session_state.participant_id}")
    st.info("💾 Your progress is automatically saved.")
