"""
Participant Session Manager
─────────────────────────────────────────────────────────────────────────────
Manages participant ID generation and session state for the user study.

Features:
- Auto-generates sequential participant IDs (P001, P002, ...)
- Tracks progress through study phases
- Persists session state across apps using temporary file
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime


# Session file to persist participant ID across apps
SESSION_FILE = Path("study_data/.active_session.json")


def get_next_participant_id(study_data_dir: str = "study_data") -> str:
    """
    Generate next sequential participant ID (P001, P002, ...).
    
    Reads existing demographics.csv to find the highest ID and increments.
    Thread-safe for in-person studies (one session at a time).
    """
    study_path = Path(study_data_dir)
    demographics_file = study_path / "demographics.csv"
    
    if not demographics_file.exists():
        return "P001"
    
    # Read existing IDs
    with open(demographics_file, 'r') as f:
        lines = f.readlines()
        if len(lines) <= 1:  # Only header or empty
            return "P001"
        
        # Extract last participant ID
        last_line = lines[-1].strip()
        if not last_line:
            return "P001"
        
        # Get first column (participant_id)
        last_id = last_line.split(',')[0]
        
        # Extract number and increment
        try:
            num = int(last_id[1:])  # Remove 'P' prefix
            return f"P{num + 1:03d}"
        except (ValueError, IndexError):
            return "P001"


def initialize_session():
    """
    Initialize session state variables for tracking study progress.
    
    Call this at the start of each app (variant A and variant B).
    If an active session exists from previous app, restore it.
    """
    # Try to restore from file if session is new
    if 'participant_id' not in st.session_state or st.session_state.participant_id is None:
        restore_session_from_file()
    
    # Initialize defaults if still not set
    if 'participant_id' not in st.session_state:
        st.session_state.participant_id = None
    
    if 'demographics_completed' not in st.session_state:
        st.session_state.demographics_completed = False
    
    if 'current_task_index' not in st.session_state:
        st.session_state.current_task_index = 0
    
    if 'tasks_completed' not in st.session_state:
        st.session_state.tasks_completed = []
    
    if 'variant_completed' not in st.session_state:
        st.session_state.variant_completed = False
    
    if 'study_start_time' not in st.session_state:
        st.session_state.study_start_time = datetime.now()


def save_session_to_file():
    """
    Save current participant ID to file so it persists across apps.
    Call this when moving from Variant A to Variant B.
    """
    if st.session_state.participant_id:
        SESSION_FILE.parent.mkdir(exist_ok=True)
        session_data = {
            'participant_id': st.session_state.participant_id,
            'demographics_completed': st.session_state.demographics_completed,
            'timestamp': datetime.now().isoformat()
        }
        with open(SESSION_FILE, 'w') as f:
            json.dump(session_data, f, indent=2)


def restore_session_from_file():
    """
    Restore participant ID from file if it exists.
    Call this when starting Variant B to continue from Variant A.
    """
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, 'r') as f:
                session_data = json.load(f)
            
            st.session_state.participant_id = session_data.get('participant_id')
            st.session_state.demographics_completed = session_data.get('demographics_completed', True)
            
        except (json.JSONDecodeError, IOError):
            # If file is corrupted, ignore it
            pass


def clear_session_file():
    """
    Clear the session file after study is fully complete.
    Call this after Section F (final feedback) is done.
    """
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()


def start_new_participant():
    """
    Generate new participant ID and reset session state for new session.
    """
    st.session_state.participant_id = get_next_participant_id()
    st.session_state.demographics_completed = False
    st.session_state.current_task_index = 0
    st.session_state.tasks_completed = []
    st.session_state.variant_completed = False
    st.session_state.study_start_time = datetime.now()


def mark_task_completed(task_id: str):
    """Mark a specific task as completed."""
    if task_id not in st.session_state.tasks_completed:
        st.session_state.tasks_completed.append(task_id)


def get_study_progress() -> dict:
    """
    Get current study progress metrics.
    
    Returns:
        dict: Progress information including participant ID, tasks completed, etc.
    """
    return {
        'participant_id': st.session_state.participant_id,
        'demographics_completed': st.session_state.demographics_completed,
        'tasks_completed': len(st.session_state.tasks_completed),
        'variant_completed': st.session_state.variant_completed,
        'duration_minutes': (datetime.now() - st.session_state.study_start_time).total_seconds() / 60
    }


def go_back_to_previous_task():
    """
    Navigate back to the previous task.
    Resets the current task state so participant can re-do it.
    """
    if st.session_state.current_task_index > 0:
        st.session_state.current_task_index -= 1
        
        # Get the previous task ID (need to know which variant we're in)
        # This will be called with the task list from the calling app
        return True
    return False


def reset_task_state(task_id: str):
    """
    Reset the state flags for a specific task so it can be redone.
    """
    # Variant A flags
    if f"prediction_shown_{task_id}" in st.session_state:
        st.session_state[f"prediction_shown_{task_id}"] = False
    if f"ready_for_confidence_{task_id}" in st.session_state:
        st.session_state[f"ready_for_confidence_{task_id}"] = False
    
    # Variant B flags
    if f"prediction_shown_b_{task_id}" in st.session_state:
        st.session_state[f"prediction_shown_b_{task_id}"] = False
    if f"ready_for_confidence_b_{task_id}" in st.session_state:
        st.session_state[f"ready_for_confidence_b_{task_id}"] = False
    
    # Remove from completed tasks
    if task_id in st.session_state.tasks_completed:
        st.session_state.tasks_completed.remove(task_id)
