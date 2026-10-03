"""
Questionnaire Form Components
─────────────────────────────────────────────────────────────────────────────
Reusable form components for the user study questionnaires.

Sections:
- Section A: Demographics (7 questions)
- Section B: SUS (10 items)
- Section C: Trust (5 items)
- Section D: Understanding (5 items)
- Section E: Decision Confidence (4 items per task)
- Section F: Qualitative Feedback (4 open-ended questions)
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
from typing import Dict, List, Optional


# ── Section A: Demographics ────────────────────────────────────────────────────


def render_demographics_form() -> Optional[Dict]:
    """
    Render Section A: Demographics questionnaire.
    
    Returns:
        dict: Demographics responses, or None if form incomplete
    """
    st.subheader("📋 Section A: Participant Information")
    st.markdown("Please provide some background information about yourself.")
    st.markdown("---")
    
    with st.form("demographics_form"):
        age_group = st.selectbox(
            "1. Age group:",
            options=["", "18-29", "30-39", "40-49", "50-59", "60+"],
            index=0
        )
        
        gender = st.selectbox(
            "2. Gender:",
            options=["", "Male", "Female", "Non-binary", "Prefer not to say"],
            index=0
        )
        
        education_level = st.selectbox(
            "3. Education level:",
            options=["", "Bachelor's degree", "Master's degree", "Doctoral degree (PhD/EdD)", "Other"],
            index=0
        )
        
        role = st.text_input(
            "4. Current role in higher education:",
            placeholder="e.g., academic tutor, lecturer, academic advisor",
            help="Describe your current position"
        )
        
        years_experience = st.selectbox(
            "5. Years of experience in higher education:",
            options=["", "0-2 years", "3-5 years", "6-10 years", "11-15 years", "16+ years"],
            index=0
        )
        
        ai_experience = st.selectbox(
            "6. Experience with AI systems:",
            options=["", 
                     "None (never used AI-based systems)",
                     "Basic (aware of AI systems, minimal hands-on use)",
                     "Moderate (regularly use AI-based tools)",
                     "Advanced (extensive experience, understand underlying concepts)"],
            index=0
        )
        
        decision_tools = st.radio(
            "7. Familiarity with data-driven decision tools:",
            options=["", "Yes (have used analytics/dashboards/data systems to inform decisions)", 
                     "No (have not used such tools)"],
            index=0
        )
        
        submitted = st.form_submit_button("Continue to Study ➔", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            if not all([age_group, gender, education_level, role.strip(), 
                       years_experience, ai_experience, decision_tools]):
                st.error("Please complete all fields before continuing.")
                return None
            
            # Map experience levels to numeric scale for logger compatibility
            ai_exp_map = {
                "None (never used AI-based systems)": 1,
                "Basic (aware of AI systems, minimal hands-on use)": 2,
                "Moderate (regularly use AI-based tools)": 3,
                "Advanced (extensive experience, understand underlying concepts)": 4
            }
            
            return {
                'age_group': age_group,
                'gender': gender,
                'education_level': education_level,
                'role': role.strip(),
                'years_experience': years_experience,
                'ai_experience': ai_exp_map.get(ai_experience, 2),
                'familiarity_with_analytics': 5 if "Yes" in decision_tools else 1
            }
    
    return None


# ── Section B: SUS ─────────────────────────────────────────────────────────────


def render_sus_form() -> Optional[List[int]]:
    """
    Render Section B: System Usability Scale (10 items).
    
    Returns:
        list: 10 Likert responses (1-5), or None if incomplete
    """
    st.subheader("📊 System Usability")
    st.markdown("Please rate your experience with the system you just used.")
    st.markdown("**Scale:** 1 = Strongly Disagree | 5 = Strongly Agree")
    st.markdown("---")
    
    items = [
        "I think that I would like to use this system frequently.",
        "I found the system unnecessarily complex.",
        "I thought the system was easy to use.",
        "I think that I would need the support of a technical person to use this system.",
        "I found the various functions in this system were well integrated.",
        "I thought there was too much inconsistency in this system.",
        "I would imagine that most people would learn to use this system very quickly.",
        "I found the system very cumbersome to use.",
        "I felt very confident using the system.",
        "I needed to learn a lot of things before I could get going with this system."
    ]
    
    with st.form("sus_form"):
        responses = []
        
        for i, item in enumerate(items, 1):
            response = st.radio(
                f"**{i}.** {item}",
                options=[None, 1, 2, 3, 4, 5],
                format_func=lambda x: "Select..." if x is None else ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"][x-1],
                horizontal=True,
                key=f"sus_{i}",
                index=0  # Default to "Select..."
            )
            responses.append(response)
            st.markdown("")
        
        submitted = st.form_submit_button("Submit SUS Responses", type="primary", use_container_width=True)
        
        if submitted:
            if None in responses:
                st.error("Please respond to all items before submitting.")
                return None
            return responses
    
    return None


# ── Section C: Trust ───────────────────────────────────────────────────────────


def render_trust_form() -> Optional[List[int]]:
    """
    Render Section C: Trust in AI System (5 items).
    
    Returns:
        list: 5 Likert responses (1-5), or None if incomplete
    """
    st.subheader("🤝 Trust in AI System")
    st.markdown("Please rate your level of trust in the system.")
    st.markdown("**Scale:** 1 = Strongly Disagree | 5 = Strongly Agree")
    st.markdown("---")
    
    items = [
        "I trust the predictions provided by the system.",
        "I feel confident relying on the system's recommendations.",
        "The system provides sufficient information to justify its predictions.",
        "I believe the system is reliable in supporting decision-making.",
        "I would use this system to support real academic decisions."
    ]
    
    with st.form("trust_form"):
        responses = []
        
        for i, item in enumerate(items, 1):
            response = st.radio(
                f"**{i}.** {item}",
                options=[None, 1, 2, 3, 4, 5],
                format_func=lambda x: "Select..." if x is None else ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"][x-1],
                horizontal=True,
                key=f"trust_{i}",
                index=0  # Default to "Select..."
            )
            responses.append(response)
            st.markdown("")
        
        submitted = st.form_submit_button("Submit Trust Responses", type="primary", use_container_width=True)
        
        if submitted:
            if None in responses:
                st.error("Please respond to all items before submitting.")
                return None
            return responses
    
    return None


# ── Section D: Understanding ───────────────────────────────────────────────────


def render_understanding_form() -> Optional[List[int]]:
    """
    Render Section D: Perceived Understanding (5 items).
    
    Returns:
        list: 5 Likert responses (1-5), or None if incomplete
    """
    st.subheader("💡 Perceived Understanding")
    st.markdown("Please rate how well you understood the system's explanations.")
    st.markdown("**Scale:** 1 = Strongly Disagree | 5 = Strongly Agree")
    st.markdown("---")
    
    items = [
        "I understand how the system arrived at its prediction.",
        "The explanation provided by the system is clear and understandable.",
        "The explanation helped me interpret the prediction effectively.",
        "I can identify which factors influenced the prediction.",
        "The explanation improved my overall understanding of the system's output."
    ]
    
    with st.form("understanding_form"):
        responses = []
        
        for i, item in enumerate(items, 1):
            response = st.radio(
                f"**{i}.** {item}",
                options=[None, 1, 2, 3, 4, 5],
                format_func=lambda x: "Select..." if x is None else ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"][x-1],
                horizontal=True,
                key=f"understanding_{i}",
                index=0  # Default to "Select..."
            )
            responses.append(response)
            st.markdown("")
        
        submitted = st.form_submit_button("Submit Understanding Responses", type="primary", use_container_width=True)
        
        if submitted:
            if None in responses:
                st.error("Please respond to all items before submitting.")
                return None
            return responses
    
    return None
        
        if submitted:
            if None in responses or 0 in responses:
                st.error("Please respond to all items.")
                return None
            return responses
    
    return None


# ── Section E: Decision Confidence ─────────────────────────────────────────────


def render_decision_confidence_form(task_case_id: str) -> Optional[List[int]]:
    """
    Render Section E: Decision Confidence (4 items per task).
    
    Args:
        task_case_id: ID of the task case (e.g., "high_risk_1")
    
    Returns:
        list: 4 Likert responses (1-5), or None if incomplete
    """
    st.subheader(f"Decision Confidence")
    st.markdown(f"Please rate your confidence in the decision you just made for **{task_case_id}**.")
    st.markdown("**Scale:** 1 = Strongly Disagree | 5 = Strongly Agree")
    st.markdown("---")
    
    items = [
        "I feel confident in the decision I made using the system.",
        "The system helped me make a more informed decision.",
        "I would be comfortable making similar decisions using this system in the future.",
        "The explanation increased my confidence in my decision."
    ]
    
    with st.form(f"confidence_form_{task_case_id}"):
        responses = []
        
        for i, item in enumerate(items, 1):
            response = st.radio(
                f"**{i}.** {item}",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"][x-1],
                horizontal=True,
                key=f"conf_{task_case_id}_{i}"
            )
            responses.append(response)
            st.markdown("")
        
        submitted = st.form_submit_button("Submit & Continue", type="primary", use_container_width=True)
        
        if submitted:
            if None in responses or 0 in responses:
                st.error("Please respond to all items.")
                return None
            return responses
    
    return None


# ── Section F: Qualitative Feedback ────────────────────────────────────────────


def render_qualitative_form() -> Optional[Dict[str, str]]:
    """
    Render Section F: Qualitative Feedback (4 open-ended questions).
    
    Administered once at the END of the study, after both variants.
    
    Returns:
        dict: Qualitative responses, or None if incomplete
    """
    st.subheader("💬 Additional Feedback")
    st.markdown("Please share your thoughts about the system (both interfaces).")
    st.markdown("---")
    
    with st.form("qualitative_form"):
        q1 = st.text_area(
            "1. What did you find most useful about the system?",
            height=100,
            placeholder="Please describe what aspects you found helpful..."
        )
        
        q2 = st.text_area(
            "2. What challenges did you experience while using the system?",
            height=100,
            placeholder="Please describe any difficulties or confusion..."
        )
        
        q3 = st.text_area(
            "3. How can the explanation interface be improved?",
            height=100,
            placeholder="Please suggest improvements..."
        )
        
        q4_preference = st.radio(
            "4. Which interface did you prefer?",
            options=["", "Static (Variant A - prediction only)", "Progressive (Variant B - with explanations)"],
            index=0
        )
        
        q4_reason = st.text_area(
            "Why did you prefer that interface?",
            height=100,
            placeholder="Please explain your preference..."
        )
        
        submitted = st.form_submit_button("Submit Final Feedback", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            if not all([q1.strip(), q2.strip(), q3.strip(), q4_preference, q4_reason.strip()]):
                st.error("⚠️ Please complete all fields.")
                return None
            
            return {
                'q1_most_useful': q1.strip(),
                'q2_challenges': q2.strip(),
                'q3_improvements': q3.strip(),
                'q4_preference': q4_preference,
                'q4_preference_reason': q4_reason.strip()
            }
    
    return None
