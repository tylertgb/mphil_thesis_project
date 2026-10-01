"""
Section F: Final Qualitative Feedback
─────────────────────────────────────────────────────────────────────────────
Standalone app for collecting Section F responses after both variants.

Administered ONCE at the very end of the study, after participant has used
both Variant A and Variant B.
─────────────────────────────────────────────────────────────────────────────
Run:  streamlit run interfaces/final_feedback_app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from interfaces.shared_components.participant_session import initialize_session, clear_session_file
from interfaces.shared_components.questionnaire_forms import render_qualitative_form
from study_response_logger import StudyResponseLogger

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Final Feedback - Study Complete",
    page_icon="✅",
    layout="centered",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F7FAFC; }
    .divider { margin: 24px 0; border-top: 1px solid #E2E8F0; }
</style>
""", unsafe_allow_html=True)

# ── Initialize session ─────────────────────────────────────────────────────────
initialize_session()

# ── Initialize logger ──────────────────────────────────────────────────────────
logger = StudyResponseLogger(output_dir="study_data")

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("✅ Final Feedback")
st.caption("User Study - Section F")
st.markdown("---")

# Check if participant ID exists
if st.session_state.participant_id is None:
    st.error("⚠️ No participant session found.")
    st.info("Please ensure you've completed both Variant A and Variant B before accessing this page.")
    
    if st.button("Manual Entry - Researcher Only", type="secondary"):
        manual_id = st.text_input("Enter Participant ID:", placeholder="e.g., P001")
        if manual_id:
            st.session_state.participant_id = manual_id
            st.rerun()
    
    st.stop()

# Show participant ID
st.info(f"**Participant ID:** {st.session_state.participant_id}")
st.markdown("---")

# Check if already completed
if 'final_feedback_completed' not in st.session_state:
    st.session_state.final_feedback_completed = False

if not st.session_state.final_feedback_completed:
    st.markdown("""
    **You have now completed both interface variants (A and B).**
    
    Please answer the following questions reflecting on your overall experience with both systems.
    """)
    st.markdown("---")
    
    qualitative_responses = render_qualitative_form()
    
    if qualitative_responses:
        # Log qualitative feedback
        logger.log_qualitative_feedback(
            st.session_state.participant_id,
            **qualitative_responses
        )
        
        st.session_state.final_feedback_completed = True
        
        # Clear session file - study is complete
        clear_session_file()
        
        st.success("✅ Final feedback saved successfully!")
        st.balloons()
        st.rerun()

else:
    # Already completed
    st.success("✅ **Study Complete!**")
    st.markdown("---")
    
    st.markdown(f"""
    **Thank you for participating in this research study!**
    
    All your responses have been recorded.
    
    **Participant ID:** {st.session_state.participant_id}
    
    Please inform the researcher that you have completed the study.
    """)
    
    st.markdown("---")
    st.caption("You may now close this window.")
