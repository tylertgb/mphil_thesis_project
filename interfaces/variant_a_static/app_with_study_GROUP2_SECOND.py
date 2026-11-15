"""
Variant A — Static Interface (GROUP 2 - SECOND Interface)
─────────────────────────────────────────────────────────────────────────────
Multi-page study flow:
  0. Participant ID entry (SECOND INTERFACE - requires ID from Progressive)
  1. Task Case 1 → Prediction + SHAP Chart → Decision Confidence
  2. Task Case 2 → Prediction + SHAP Chart → Decision Confidence
  3. Task Case 3 → Prediction + SHAP Chart → Decision Confidence
  4. SUS + Trust + Understanding questionnaires
  5. Thank you + Next steps

Shows: prediction label, probability, and SHAP bar chart (all at once, fixed layout).
This is the baseline static condition.

COUNTERBALANCING:
- This is the SECOND interface for Group 2 (participants 17-31)
- Order: Progressive (PREVIOUS) → Static (THIS)
- Requires participant ID with _G2 suffix
- order_group = "group2_progressive_first"
─────────────────────────────────────────────────────────────────────────────
Deployment: Create new Streamlit app pointing to this file
Suggested URL: mphil-study-static-second or mphil-study-group2-part2
"""

import sys
from pathlib import Path
import json

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from xai.shap_explainer import load_artefacts, explain
from xai.explainer_utils import shap_bar_chart
from interfaces.shared_components.participant_session import (
    initialize_session, mark_task_completed, get_study_progress,
    save_session_to_file, reset_task_state
)
from interfaces.shared_components.questionnaire_forms import (
    render_sus_form, render_trust_form,
    render_understanding_form, render_decision_confidence_form
)
from utils.dual_logger import DualLogger
import pandas as pd

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Risk Prediction Study - Static Interface",
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

# Define task assignment (3 cases for Variant A)
VARIANT_A_TASKS = ["high_risk_1", "medium_risk_4", "low_risk_7"]

# ── Load model artefacts (cached) ──────────────────────────────────────────────
@st.cache_resource
def get_artefacts():
    return load_artefacts()

model, scaler, feature_names = get_artefacts()

# ── Initialize logger with GROUP 2 order group ─────────────────────────────────
logger = DualLogger(output_dir="study_data", order_group="group2_progressive_first")

# ── Study Flow State Machine ───────────────────────────────────────────────────

# START: Require participant ID from Progressive (must have _G2 suffix)
if st.session_state.participant_id is None:
    st.title("Student Risk Prediction Study")
    st.markdown("### Part 2: Static Interface (Second)")
    st.markdown("---")
    
    st.info("**Welcome to Part 2!** You'll now use a second interface to review different student profiles.")
    
    st.markdown("""
    ### What You'll Do:
    
    1. **Review 3 student profiles** (10 minutes)
       - Each student's data is preloaded in the system
       - Review the prediction and provide your feedback
    
    2. **Evaluate your experience** (3 minutes)
    
    3. **Then complete Final Feedback** (5 minutes)
    
    ---
    
    **Estimated time:** 18 minutes
    """)
    
    st.markdown("---")
    st.warning("⚠️ Participant ID Required")
    st.info("Please enter your Participant ID from Part 1 (Progressive Interface) to continue.")
    
    with st.form("participant_id_form"):
        st.markdown("### Enter Your Participant ID")
        st.caption("Your Participant ID was shown at the end of Part 1 (e.g., P_20261115_143052_G2)")
        
        participant_id_input = st.text_input(
            "Participant ID",
            placeholder="P_20261115_143052_G2",
            help="Enter the ID you received after completing Part 1 (must end with _G2)"
        ).strip().upper()
        
        submit_btn = st.form_submit_button("Continue to Part 2", type="primary", use_container_width=True)
        
        if submit_btn:
            # Validate participant ID
            if not participant_id_input:
                st.error("Please enter your Participant ID")
            elif not participant_id_input.startswith("P_"):
                st.error("Invalid Participant ID format. Must start with 'P_'")
            elif not participant_id_input.endswith("_G2"):
                st.error("⚠️ Invalid Participant ID. This interface is for Group 2 participants only (ID must end with '_G2')")
                st.info("If you completed Part 1 (Progressive first), your ID should end with '_G2'. Please check your ID and try again.")
            else:
                # Valid Group 2 participant ID
                st.session_state.participant_id = participant_id_input
                st.session_state.demographics_completed = True  # Already collected in Part 1
                st.success(f"Welcome back, {participant_id_input}!")
                st.rerun()
    
    st.stop()

# Show progress
st.caption(f"Participant ID: {st.session_state.participant_id} | Group 2: Static (Second)")

# ── Phase 1: Task Cases ────────────────────────────────────────────────────────

current_task_idx = st.session_state.current_task_index

if current_task_idx < len(VARIANT_A_TASKS):
    task_id = VARIANT_A_TASKS[current_task_idx]
    task_case = next(case for case in TASK_CASES if case['case_id'] == task_id)
    
    # Show progress bar
    progress_pct = (current_task_idx / len(VARIANT_A_TASKS)) * 100
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress_pct}%"></div>
    </div>
    <p style="text-align:center; color:#718096; font-size:0.9rem;">
        Task {current_task_idx + 1} of {len(VARIANT_A_TASKS)}: {task_case['risk_category']}
    </p>
    """, unsafe_allow_html=True)
    
    st.title("Student Risk Prediction")
    st.caption("Educational Decision-Support System  ·  Static Interface")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Initialize state flags
    if f"prediction_shown_{task_id}" not in st.session_state:
        st.session_state[f"prediction_shown_{task_id}"] = False
    if f"ready_for_confidence_{task_id}" not in st.session_state:
        st.session_state[f"ready_for_confidence_{task_id}"] = False
    
    # State 1: Show profile + "Get Prediction" button
    if not st.session_state[f"prediction_shown_{task_id}"]:
        st.info(f"**Scenario:** Review the student profile below and view the risk prediction.")
        
        # Pre-fill form with task case data
        features = task_case['features']
        
        with st.expander("📊 Student Profile (Click to expand)", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Credits Studied", f"{features['studied_credits']:.0f}")
                st.metric("Previous Attempts", f"{features['num_of_prev_attempts']:.0f}")
                st.metric("Avg Assessment Score", f"{features.get('avg_assessment_score', 'N/A')}")
                st.metric("Assessments Completed", f"{features['num_assessments_completed']:.0f}")
                st.metric("Assessments Due", f"{features['num_assessments_due']:.0f}")
            
            with col2:
                st.metric("Completion Rate", f"{features['completion_rate']:.0%}")
                st.metric("Total VLE Clicks", f"{features['total_clicks_pre_cutoff']:.0f}")
                st.metric("Activities Accessed", f"{features['num_activities_accessed']:.0f}")
                st.metric("Days Active", f"{features['days_active']:.0f}")
                st.metric("Avg Clicks/Day", f"{features['avg_clicks_per_active_day']:.1f}")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Navigation buttons at bottom
        if current_task_idx > 0:
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("⬅️ Back", use_container_width=True, key=f"back_btn_{task_id}_s1"):
                    # Go back to previous task
                    st.session_state.current_task_index -= 1
                    prev_task_id = VARIANT_A_TASKS[st.session_state.current_task_index]
                    reset_task_state(prev_task_id)
                    st.rerun()
            with col2:
                if st.button("Get Risk Prediction", type="primary", use_container_width=True):
                    st.session_state[f"prediction_shown_{task_id}"] = True
                    st.rerun()
        else:
            # First task - no back button
            if st.button("Get Risk Prediction", type="primary", use_container_width=True):
                st.session_state[f"prediction_shown_{task_id}"] = True
                st.rerun()
    
    # State 2: Show prediction + SHAP chart + "Continue" button
    elif not st.session_state[f"ready_for_confidence_{task_id}"]:
        # Get actual SHAP explanation for this task case
        features = task_case['features']
        student_df = pd.DataFrame([features])
        explanation = explain(student_df, model, scaler, feature_names)
        
        # Extract values
        prob = explanation['probability']
        label = explanation['label']
        shap_values = explanation['shap_values']
        is_at_risk = explanation['prediction'] == 0
        
        box_class = "at-risk" if is_at_risk else "success"
        emoji = "⚠" if is_at_risk else "✓"
        color = "#C53030" if is_at_risk else "#276749"
        prob_display = (1 - prob) if is_at_risk else prob
        
        # Show prediction
        st.markdown(f"""
        <div class="risk-box {box_class}">
            <div class="risk-label" style="color:{color};">{emoji} Predicted: {label}</div>
            <div class="risk-prob">Confidence: {prob_display:.1%}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Show SHAP bar chart (static, always visible)
        st.markdown("### Feature Impact on Prediction")
        st.caption("This chart shows which student characteristics most influenced the prediction:")
        
        # Generate and display SHAP bar chart
        fig_bar = shap_bar_chart(
            shap_values, top_n=10, title="Top 10 Feature Contributions (SHAP Values)"
        )
        st.pyplot(fig_bar, use_container_width=True)
        
        # Legend
        st.markdown("""
        <div style="display: flex; gap: 24px; margin: 12px 0; font-size: 0.85rem; color: #4A5568;">
            <div>
                <span style="display: inline-block; width: 14px; height: 14px; background: #FC8181; border-radius: 2px; margin-right: 6px;"></span>
                Increases risk (pushes toward At-Risk)
            </div>
            <div>
                <span style="display: inline-block; width: 14px; height: 14px; background: #68D391; border-radius: 2px; margin-right: 6px;"></span>
                Decreases risk (pushes toward Success)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        st.info("**Please review the prediction and explanation above, then click Continue to provide your feedback.**")
        
        # Navigation buttons at bottom
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⬅️ Back", use_container_width=True, key=f"back_btn_{task_id}_s2"):
                # Go back to profile view
                st.session_state[f"prediction_shown_{task_id}"] = False
                st.rerun()
        with col2:
            if st.button("Continue to Questionnaire ➔", type="primary", use_container_width=True, key=f"continue_to_conf_{task_id}"):
                st.session_state[f"ready_for_confidence_{task_id}"] = True
                st.rerun()
    
    # State 3: Show confidence questionnaire
    else:
        st.info(f"You've reviewed the prediction for this student. Please complete the decision confidence questionnaire.")
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        confidence_responses = render_decision_confidence_form(task_id)
        
        # Back button at bottom (before form submission)
        if not confidence_responses:  # Only show if form not submitted
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            if st.button("⬅️ Back", use_container_width=False, key=f"back_btn_{task_id}_s3"):
                # Go back to prediction view
                st.session_state[f"ready_for_confidence_{task_id}"] = False
                st.rerun()
        
        if confidence_responses:
            # Log decision confidence (logger already has order_group set)
            logger.log_decision_confidence(
                st.session_state.participant_id,
                "variant_a",
                task_id,
                confidence_responses
            )
            
            # Mark task as completed
            mark_task_completed(task_id)
            st.session_state.current_task_index += 1
            
            st.success(f"Task {current_task_idx + 1} completed!")
            st.rerun()

# ── Phase 2: Post-Variant Questionnaires ───────────────────────────────────────
elif not st.session_state.variant_completed:
    st.title("System Evaluation")
    st.markdown("Please complete the following questionnaires about your experience with the Static Interface.")
    st.markdown("---")
    
    # Check which questionnaires are completed
    if 'sus_completed_a' not in st.session_state:
        st.session_state.sus_completed_a = False
    if 'trust_completed_a' not in st.session_state:
        st.session_state.trust_completed_a = False
    if 'understanding_completed_a' not in st.session_state:
        st.session_state.understanding_completed_a = False
    
    # SUS
    if not st.session_state.sus_completed_a:
        sus_responses = render_sus_form()
        if sus_responses:
            logger.log_sus(st.session_state.participant_id, "variant_a", sus_responses)
            st.session_state.sus_completed_a = True
            st.success("SUS responses saved!")
            st.rerun()
        st.stop()
    
    # Trust
    if not st.session_state.trust_completed_a:
        trust_responses = render_trust_form()
        if trust_responses:
            logger.log_trust(st.session_state.participant_id, "variant_a", trust_responses)
            st.session_state.trust_completed_a = True
            st.success("Trust responses saved!")
            st.rerun()
        st.stop()
    
    # Understanding
    if not st.session_state.understanding_completed_a:
        understanding_responses = render_understanding_form()
        if understanding_responses:
            logger.log_understanding(st.session_state.participant_id, "variant_a", understanding_responses)
            st.session_state.understanding_completed_a = True
            st.session_state.variant_completed = True
            
            # Set variant name for session tracking
            st.session_state.variant_name = "variant_a"
            
            # Save session to file
            save_session_to_file()
            
            st.success("All responses saved for Static Interface!")
            st.rerun()
        st.stop()

# ── Phase 3: Completion & Next Steps ───────────────────────────────────────────
else:
    st.title("Part 2 (Static Interface) Completed!")
    st.markdown("---")
    
    st.success(f"""
    **Thank you for completing Part 2!**
    
    You have finished:
    - {len(VARIANT_A_TASKS)} task cases
    - 3 evaluation questionnaires
    """)
    
    st.markdown("### 🎉 Final Step: Complete the Comparison Questionnaire")
    st.markdown("Please click the button below to share your overall feedback comparing both interfaces:")
    
    st.markdown("")  # Spacing
    
    # Red Streamlit-style button that opens in new tab
    st.link_button(
        "Open Final Feedback Form",
        "https://mphil-study-final-feedback.streamlit.app",
        use_container_width=True,
        type="primary"
    )
    
    st.markdown("""
    
    This is the last part of the study where you'll compare both interfaces (Progressive vs Static).
    
    ---
    
    **Alternative: Copy this link if button doesn't work**
    ```
    https://mphil-study-final-feedback.streamlit.app
    ```
    
    ---
    """)
    
    st.info(f"Session saved: {st.session_state.participant_id}")
    st.caption("Thank you for your participation! 🙏")
