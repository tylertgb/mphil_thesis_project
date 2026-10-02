"""
Variant A — Control Interface with Integrated Study Questionnaires
─────────────────────────────────────────────────────────────────────────────
Multi-page study flow:
  1. Demographics (if first time)
  2. Task Case 1 → Prediction → Decision Confidence
  3. Task Case 2 → Prediction → Decision Confidence
  4. Task Case 3 → Prediction → Decision Confidence
  5. SUS + Trust + Understanding questionnaires
  6. Thank you + Next steps

Shows the student risk prediction label and probability.
No SHAP explanation is shown — this is the control condition.
─────────────────────────────────────────────────────────────────────────────
Deployed URL: https://mphil-study-variant-a.streamlit.app
"""

import sys
from pathlib import Path
import json

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from xai.shap_explainer import load_artefacts, explain
from interfaces.shared_components.student_form import render_form, encode_input
from interfaces.shared_components.participant_session import (
    initialize_session, start_new_participant, mark_task_completed, get_study_progress,
    save_session_to_file, reset_task_state
)
from interfaces.shared_components.questionnaire_forms import (
    render_demographics_form, render_sus_form, render_trust_form,
    render_understanding_form, render_decision_confidence_form
)
from study_response_logger import StudyResponseLogger

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Risk Prediction - Variant A",
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

# ── Initialize logger ──────────────────────────────────────────────────────────
logger = StudyResponseLogger(output_dir="study_data")

# ── Study Flow State Machine ───────────────────────────────────────────────────

# If no participant ID, show welcome screen
if st.session_state.participant_id is None:
    st.title("Student Risk Prediction Study")
    st.markdown("### Variant A: Prediction Interface")
    st.markdown("---")
    
    st.markdown("""
    **Welcome to this research study!**
    
    You will be asked to:
    1. Complete a brief demographics questionnaire
    2. Review predictions for **3 student cases**
    3. Provide feedback on your experience
    
    **Estimated time:** 10-15 minutes
    
    All responses are anonymous and will be used solely for research purposes.
    """)
    
    if st.button("Start Study", type="primary", use_container_width=True):
        start_new_participant()
        st.rerun()
    
    st.stop()

# Show progress
progress = get_study_progress()
st.caption(f"Participant ID: {st.session_state.participant_id} | Variant A")

# ── Phase 1: Demographics ──────────────────────────────────────────────────────
if not st.session_state.demographics_completed:
    demographics_data = render_demographics_form()
    
    if demographics_data:
        logger.log_demographics(st.session_state.participant_id, demographics_data)
        st.session_state.demographics_completed = True
        st.success("✅ Demographics saved! Moving to task cases...")
        st.balloons()
        st.rerun()
    
    st.stop()

# ── Phase 2: Task Cases ────────────────────────────────────────────────────────

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
    st.caption("Educational Decision-Support System  ·  Variant A")
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
    
    # State 2: Show prediction + "Continue" button
    elif not st.session_state[f"ready_for_confidence_{task_id}"]:
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
            <div class="risk-prob">Confidence: {prob_display:.1%}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        st.info("📝 **Please review the prediction above, then click Continue to provide your feedback.**")
        
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
            # Log decision confidence
            logger.log_decision_confidence(
                st.session_state.participant_id,
                "variant_a",
                task_id,
                confidence_responses
            )
            
            # Mark task as completed
            mark_task_completed(task_id)
            st.session_state.current_task_index += 1
            
            st.success(f"✅ Task {current_task_idx + 1} completed!")
            st.rerun()

# ── Phase 3: Post-Variant Questionnaires ───────────────────────────────────────
elif not st.session_state.variant_completed:
    st.title("System Evaluation")
    st.markdown("Please complete the following questionnaires about your experience with Variant A.")
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
            st.success("✅ SUS responses saved!")
            st.rerun()
        st.stop()
    
    # Trust
    if not st.session_state.trust_completed_a:
        trust_responses = render_trust_form()
        if trust_responses:
            logger.log_trust(st.session_state.participant_id, "variant_a", trust_responses)
            st.session_state.trust_completed_a = True
            st.success("✅ Trust responses saved!")
            st.rerun()
        st.stop()
    
    # Understanding
    if not st.session_state.understanding_completed_a:
        understanding_responses = render_understanding_form()
        if understanding_responses:
            logger.log_understanding(st.session_state.participant_id, "variant_a", understanding_responses)
            st.session_state.understanding_completed_a = True
            st.session_state.variant_completed = True
            
            # Save session to file so Variant B can access it
            save_session_to_file()
            
            st.success("✅ All responses saved for Variant A!")
            st.rerun()
        st.stop()

# ── Phase 4: Completion ────────────────────────────────────────────────────────
else:
    st.title("✅ Variant A Completed!")
    st.markdown("---")
    
    st.success(f"""
    **Thank you for completing Variant A!**
    
    You have finished:
    - {len(VARIANT_A_TASKS)} task cases
    - 3 evaluation questionnaires
    
    **Participant ID:** {st.session_state.participant_id}
    """)
    
    st.markdown("---")
    
    st.info("""
    ### 📋 Next Step: Proceed to Variant B
    
    **Please continue to the next part of the study:**
    
    Click the link below to access Variant B (Progressive Disclosure Interface):
    
    👉 **[Open Variant B - Progressive Interface](https://mphil-study-variant-b.streamlit.app)**
    
    Your session will automatically continue with your Participant ID: **{st.session_state.participant_id}**
    
    ---
    
    **Alternative Links:**
    - 🔗 [Variant B (Progressive)](https://mphil-study-variant-b.streamlit.app)
    - 📝 [Final Feedback Form](https://mphil-study-final-feedback.streamlit.app) *(complete after Variant B)*
    """)
    
    st.markdown("---")
    st.success(f"✅ Session saved: {st.session_state.participant_id}")
    st.info("💾 Your progress is automatically saved. You can continue on any device.")

