"""
Dual Logger - GitHub API + CSV Fallback
─────────────────────────────────────────────────────────────────────────────
Automatically uses GitHub API when configured, falls back to CSV for local development.

This allows:
- Cloud deployments → Write to GitHub 'data' branch (no app restarts)
- Local development → Write to CSV files (no setup needed)
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
from typing import Dict, List, Any
from pathlib import Path

# Try to import GitHub logger
try:
    from utils.github_logger import GitHubLogger
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

# Always import CSV logger as fallback
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from study_response_logger import StudyResponseLogger


class DualLogger:
    """
    Unified logging interface that writes to both GitHub and CSV.
    
    Priority:
    1. GitHub API (if configured) - for cloud deployment
    2. CSV files (always) - for backup and local development
    """
    
    def __init__(self, output_dir: str = "study_data"):
        """Initialize both loggers"""
        self.csv_logger = StudyResponseLogger(output_dir)
        
        # Check if GitHub API is configured
        self.github_enabled = False
        if GITHUB_AVAILABLE:
            try:
                if "GITHUB_TOKEN" in st.secrets:
                    self.github_logger = GitHubLogger()
                    if self.github_logger.enabled:
                        self.github_enabled = True
            except Exception as e:
                pass  # Silently fall back to CSV
    
    def log_demographics(self, participant_id: str, demographics: Dict[str, Any]):
        """Log demographics to both GitHub and CSV"""
        # Always log to CSV
        self.csv_logger.log_demographics(participant_id, demographics)
        
        # Try GitHub if enabled
        if self.github_enabled:
            try:
                self.github_logger.log_demographics(participant_id, demographics)
            except Exception as e:
                pass  # Silently continue with CSV backup
    
    def log_sus(self, participant_id: str, condition: str, responses: List[int]):
        """Log SUS responses to both systems"""
        # Always log to CSV
        self.csv_logger.log_sus(participant_id, condition, responses)
        
        # Try GitHub if enabled
        if self.github_enabled:
            try:
                self.github_logger.log_sus(participant_id, condition, responses)
            except Exception as e:
                pass  # Silently continue with CSV backup
    
    def log_trust(self, participant_id: str, condition: str, responses: List[int]):
        """Log trust responses to both systems"""
        # Always log to CSV
        self.csv_logger.log_trust(participant_id, condition, responses)
        
        # Try GitHub if enabled
        if self.github_enabled:
            try:
                self.github_logger.log_trust(participant_id, condition, responses)
            except Exception as e:
                pass  # Silently continue with CSV backup
    
    def log_understanding(self, participant_id: str, condition: str, responses: List[int]):
        """Log understanding responses to both systems"""
        # Always log to CSV
        self.csv_logger.log_understanding(participant_id, condition, responses)
        
        # Try GitHub if enabled
        if self.github_enabled:
            try:
                self.github_logger.log_understanding(participant_id, condition, responses)
            except Exception as e:
                pass  # Silently continue with CSV backup
    
    def log_decision_confidence(
        self, 
        participant_id: str, 
        condition: str, 
        task_case_id: str, 
        responses: List[int]
    ):
        """Log decision confidence to both systems"""
        # Always log to CSV
        self.csv_logger.log_decision_confidence(
            participant_id, condition, task_case_id, responses
        )
        
        # Try GitHub if enabled
        if self.github_enabled:
            try:
                self.github_logger.log_decision_confidence(
                    participant_id, condition, task_case_id, responses
                )
            except Exception as e:
                pass  # Silently continue with CSV backup
    
    def log_qualitative_feedback(
        self,
        participant_id: str,
        q1_most_useful: str,
        q2_challenges: str,
        q3_improvements: str,
        q4_preference: str,
        q4_preference_reason: str,
    ):
        """Log qualitative feedback to both systems"""
        # Always log to CSV
        self.csv_logger.log_qualitative_feedback(
            participant_id,
            q1_most_useful,
            q2_challenges,
            q3_improvements,
            q4_preference,
            q4_preference_reason,
        )
        
        # Try GitHub if enabled
        if self.github_enabled:
            try:
                self.github_logger.log_qualitative_feedback(
                    participant_id,
                    q1_most_useful,
                    q2_challenges,
                    q3_improvements,
                    q4_preference,
                    q4_preference_reason,
                )
            except Exception as e:
                pass  # Silently continue with CSV backup
    
    def log_session_metadata(
        self,
        participant_id: str,
        order: str,
        duration_minutes: int = None,
        task_cases_shown: List[str] = None,
        notes: str = None,
    ):
        """Log session metadata (CSV only)"""
        self.csv_logger.log_session_metadata(
            participant_id, order, duration_minutes, task_cases_shown, notes
        )
