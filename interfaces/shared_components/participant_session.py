"""
Participant Session Manager
─────────────────────────────────────────────────────────────────────────────
Manages participant ID generation and session state for the user study.

Features:
- Auto-generates sequential participant IDs (P001, P002, ...)
- Tracks progress through study phases
- Persists session state across apps using GitHub API (separate data branch)
- No app restarts (data branch isolated from code)
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
from pathlib import Path
import csv
import requests
import base64
import json
from io import StringIO
from datetime import datetime, timedelta


# Session tracking via GitHub API (persists across deployed apps)
SESSIONS_FILE = Path("study_data/active_sessions.csv")


def get_next_participant_id(study_data_dir: str = "study_data") -> str:
    """
    Generate unique participant ID using timestamp.
    
    Format: P_YYYYMMDD_HHMMSS (e.g., P_20241002_143052)
    This ensures true uniqueness even with concurrent users.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"P_{timestamp}"


def initialize_session():
    """
    Initialize session state variables for tracking study progress.
    
    Call this at the start of each app (variant A and variant B).
    
    NOTE: Does NOT restore from file automatically. 
    Variant B should explicitly restore session, Variant A should start fresh.
    """
    # Initialize defaults if not set (but don't restore from file)
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


def _get_github_config():
    """Get GitHub configuration from secrets if available."""
    if "GITHUB_TOKEN" in st.secrets and "GITHUB_REPO" in st.secrets:
        return {
            "token": st.secrets["GITHUB_TOKEN"],
            "repo": st.secrets["GITHUB_REPO"],
            "branch": "data",
            "enabled": True
        }
    return {"enabled": False}


def _fetch_sessions_from_github():
    """Fetch active_sessions.csv from GitHub data branch."""
    config = _get_github_config()
    if not config["enabled"]:
        # Fallback to local CSV
        if SESSIONS_FILE.exists():
            with open(SESSIONS_FILE, 'r') as f:
                return f.read()
        return None
    
    url = f"https://api.github.com/repos/{config['repo']}/contents/study_data/active_sessions.csv"
    headers = {
        "Authorization": f"Bearer {config['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"ref": config["branch"]}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            content = base64.b64decode(response.json()["content"]).decode("utf-8")
            return content
        elif response.status_code == 404:
            return None
        else:
            st.warning(f"GitHub API error: {response.json().get('message', 'Unknown error')}")
            return None
    except Exception as e:
        st.warning(f"Failed to fetch session from GitHub: {e}")
        return None


def _save_sessions_to_github(csv_content: str):
    """Save active_sessions.csv to GitHub data branch."""
    config = _get_github_config()
    if not config["enabled"]:
        # Fallback to local CSV
        SESSIONS_FILE.parent.mkdir(exist_ok=True)
        with open(SESSIONS_FILE, 'w') as f:
            f.write(csv_content)
        return True
    
    url = f"https://api.github.com/repos/{config['repo']}/contents/study_data/active_sessions.csv"
    headers = {
        "Authorization": f"Bearer {config['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get current file SHA if exists
    sha = None
    params = {"ref": config["branch"]}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            sha = response.json()["sha"]
    except:
        pass
    
    # Encode content
    encoded_content = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    
    # Prepare payload
    payload = {
        "message": f"Update session - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "content": encoded_content,
        "branch": config["branch"]
    }
    if sha:
        payload["sha"] = sha
    
    try:
        response = requests.put(url, headers=headers, data=json.dumps(payload), timeout=10)
        if response.status_code in [200, 201]:
            return True
        else:
            st.error(f"Failed to save session: {response.json().get('message', 'Unknown')}")
            return False
    except Exception as e:
        st.error(f"GitHub session save failed: {e}")
        return False


def save_session_to_csv(participant_id: str, variant: str = "variant_a"):
    """
    Save participant session to GitHub data branch (or local CSV fallback).
    Creates or updates the active_sessions.csv file.
    
    Args:
        participant_id: Participant ID (e.g., P001)
        variant: Which variant completed (variant_a or variant_b)
    """
    # Fetch existing sessions from GitHub
    existing_content = _fetch_sessions_from_github()
    
    sessions = {}
    if existing_content:
        try:
            reader = csv.DictReader(StringIO(existing_content))
            for row in reader:
                sessions[row['participant_id']] = row
        except:
            pass
    
    # Update or add this session
    if participant_id in sessions:
        # Update existing
        sessions[participant_id][f'{variant}_completed'] = 'True'
        sessions[participant_id]['timestamp'] = datetime.now().isoformat()
    else:
        # Create new
        sessions[participant_id] = {
            'participant_id': participant_id,
            'variant_a_completed': 'True' if variant == 'variant_a' else 'False',
            'variant_b_completed': 'True' if variant == 'variant_b' else 'False',
            'timestamp': datetime.now().isoformat()
        }
    
    # Convert back to CSV
    output = StringIO()
    fieldnames = ['participant_id', 'variant_a_completed', 'variant_b_completed', 'timestamp']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for session in sessions.values():
        # Ensure all fields exist
        row = {
            'participant_id': session.get('participant_id', ''),
            'variant_a_completed': session.get('variant_a_completed', 'False'),
            'variant_b_completed': session.get('variant_b_completed', 'False'),
            'timestamp': session.get('timestamp', datetime.now().isoformat())
        }
        writer.writerow(row)
    
    csv_content = output.getvalue()
    
    # Save to GitHub (or local)
    return _save_sessions_to_github(csv_content)


def get_latest_participant_id() -> str:
    """
    Get the most recent participant ID from active sessions (from GitHub).
    Used when Variant B is opened to find the current participant.
    """
    existing_content = _fetch_sessions_from_github()
    
    if not existing_content:
        return None
    
    try:
        reader = csv.DictReader(StringIO(existing_content))
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
    except Exception as e:
        st.warning(f"Error reading sessions: {e}")
        return None


def check_variant_completed(participant_id: str, variant: str = "variant_a") -> bool:
    """
    Check if a participant has completed a specific variant.
    
    Args:
        participant_id: Participant ID (e.g., P001)
        variant: variant_a or variant_b
    
    Returns:
        True if variant completed, False otherwise
    """
    existing_content = _fetch_sessions_from_github()
    
    if not existing_content:
        return False
    
    try:
        reader = csv.DictReader(StringIO(existing_content))
        for row in reader:
            if row['participant_id'] == participant_id:
                return row.get(f'{variant}_completed', 'False') == 'True'
        return False
    except Exception as e:
        st.warning(f"Error checking variant completion: {e}")
        return False


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
        # Determine which variant was completed
        if 'variant_name' in st.session_state:
            variant = st.session_state.variant_name
        else:
            variant = "variant_a"  # Default assume Variant A
        
        save_session_to_csv(st.session_state.participant_id, variant)


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



def show_session_status():
    """
    Display session status in the UI sidebar.
    """
    if st.session_state.participant_id:
        st.sidebar.info(f"Participant: {st.session_state.participant_id}")
        
        # Show which variants completed
        variant_a_done = check_variant_completed(st.session_state.participant_id, "variant_a")
        variant_b_done = check_variant_completed(st.session_state.participant_id, "variant_b")
        
        if variant_a_done:
            st.sidebar.markdown("✓ Variant A completed")
        if variant_b_done:
            st.sidebar.markdown("✓ Variant B completed")


def validate_session_for_variant_b() -> bool:
    """
    Validate that Variant A was completed before allowing Variant B.
    
    Returns:
        True if session is valid, False if Variant A not completed
    """
    if not st.session_state.participant_id:
        # Try to load latest session
        latest_id = get_latest_participant_id()
        if latest_id:
            st.session_state.participant_id = latest_id
            st.session_state.demographics_completed = True
        else:
            st.error("No active session found. Please complete Variant A first.")
            st.info("Open the Variant A app and complete the study before accessing Variant B.")
            return False
    
    # Check if Variant A completed
    variant_a_done = check_variant_completed(st.session_state.participant_id, "variant_a")
    
    if not variant_a_done:
        st.error(f"Participant {st.session_state.participant_id} has not completed Variant A yet.")
        st.info("Please complete Variant A before proceeding to Variant B.")
        
        # Show retry button
        if st.button("Retry Loading Session", use_container_width=True):
            st.rerun()
        
        return False
    
    return True
