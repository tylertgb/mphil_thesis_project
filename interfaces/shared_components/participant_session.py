"""
Participant Session Manager
─────────────────────────────────────────────────────────────────────────────
Manages participant ID generation and session state for the user study.

Features:
- Auto-generates sequential participant IDs (P001, P002, ...)
- Tracks progress through study phases
- Persists session state across apps using CSV file (works on cloud deployment)
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
from pathlib import Path
import csv
from datetime import datetime, timedelta


# Session tracking via CSV (persists across deployed apps via GitHub)
SESSIONS_FILE = Path("study_data/active_sessions.csv")


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


def save_session_to_csv(participant_id: str):
    """
    Save participant session to CSV (works across separate Streamlit Cloud apps).
    Creates or updates the active_sessions.csv file.
    """
    SESSIONS_FILE.parent.mkdir(exist_ok=True)
    
    # Initialize file if it doesn't exist
    if not SESSIONS_FILE.exists():
        with open(SESSIONS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['participant_id', 'variant_a_completed', 'timestamp'])
    
    # Read existing sessions
    sessions = {}
    if SESSIONS_FILE.exists():
        with open(SESSIONS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sessions[row['participant_id']] = row
    
    # Update or add this session
    sessions[participant_id] = {
        'participant_id': participant_id,
        'variant_a_completed': 'True',
        'timestamp': datetime.now().isoformat()
    }
    
    # Write back
    with open(SESSIONS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['participant_id', 'variant_a_completed', 'timestamp'])
        writer.writeheader()
        for session in sessions.values():
            writer.writerow(session)


def get_latest_participant_id() -> str:
    """
    Get the most recent participant ID from active sessions.
    Used when Variant B is opened to find the current participant.
    """
    if not SESSIONS_FILE.exists():
        return None
    
    try:
        with open(SESSIONS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            sessions = list(reader)
            
            if not sessions:
                return None
            
            # Get most recent session (within last 2 hours)
            recent_sessions = []
            for session in sessions:
                try:
                    timestamp = datetime.fromisoformat(session['timestamp'])
                    if datetime.now() - timestamp < timedelta(hours=2):
                        recent_sessions.append(session)
                except (ValueError, KeyError):
                    continue
            
            if recent_sessions:
                # Return most recent
                latest = max(recent_sessions, key=lambda s: s['timestamp'])
                return latest['participant_id']
            
        return None
    except (FileNotFoundError, csv.Error):
        return None


def initialize_session():
    """
    Initialize session state variables for tracking study progress.
    
    Call this at the start of each app (variant A and variant B).
    For Variant B, tries to restore the most recent participant session.
    """
    # Try to restore from CSV if session is new (for Variant B)
    if 'participant_id' not in st.session_state or st.session_state.participant_id is None:
        latest_id = get_latest_participant_id()
        if latest_id:
            st.session_state.participant_id = latest_id
            st.session_state.demographics_completed = True
    
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
    Save current participant ID so it persists across apps.
    Call this when moving from Variant A to Variant B.
    """
    if st.session_state.participant_id:
        save_session_to_csv(st.session_state.participant_id)


def restore_session_from_file():
    """
    Restore participant ID from CSV.
    Call this when starting Variant B to continue from Variant A.
    """
    latest_id = get_latest_participant_id()
    if latest_id:
        st.session_state.participant_id = latest_id
        st.session_state.demographics_completed = True


def clear_session_file():
    """
    Clear the session tracking after study is fully complete.
    Call this after Section F (final feedback) is done.
    """
    # For cloud deployment, we keep the CSV for tracking
    # Just mark as completed in a separate column if needed
    pass


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
