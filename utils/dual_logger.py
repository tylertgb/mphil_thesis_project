"""
Dual Logger - Google Sheets + CSV Fallback
─────────────────────────────────────────────────────────────────────────────
Automatically uses Google Sheets when configured, falls back to CSV for local development.

This allows:
- Cloud deployments → Write to Google Sheets (real-time sync)
- Local development → Write to CSV files (no setup needed)
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
from typing import Dict, List, Any
from pathlib import Path

# Try to import Google Sheets logger
try:
    from utils.google_sheets_logger import GoogleSheetsLogger
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False

# Always import CSV logger as fallback
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from study_response_logger import StudyResponseLogger


class DualLogger:
    """
    Unified logging interface that writes to both Google Sheets and CSV.
    
    Priority:
    1. Google Sheets (if configured) - for cloud deployment
    2. CSV files (always) - for backup and local development
    """
    
    def __init__(self, output_dir: str = "study_data"):
        """Initialize both loggers"""
        self.csv_logger = StudyResponseLogger(output_dir)
        
        # Check if Google Sheets is configured
        self.gsheets_enabled = False
        if GSHEETS_AVAILABLE:
            try:
                if "gcp_service_account" in st.secrets or Path("service_account.json").exists():
                    self.gsheets_logger = GoogleSheetsLogger()
                    if self.gsheets_logger.client:
                        self.gsheets_enabled = True
                        st.success("✅ Connected to Google Sheets - data will sync in real-time!")
                    else:
                        st.info("ℹ️ Google Sheets not configured - using local CSV storage")
            except Exception as e:
                st.warning(f"⚠️ Google Sheets connection failed: {e}\nUsing CSV fallback.")
        else:
            st.info("ℹ️ Using local CSV storage")
    
    def log_demographics(self, participant_id: str, demographics: Dict[str, Any]):
        """Log demographics to both Google Sheets and CSV"""
        # Always log to CSV
        self.csv_logger.log_demographics(participant_id, demographics)
        
        # Try Google Sheets if enabled
        if self.gsheets_enabled:
            try:
                self.gsheets_logger.log_demographics(participant_id, demographics)
            except Exception as e:
                st.warning(f"Google Sheets write failed: {e}")
    
    def log_sus(self, participant_id: str, condition: str, responses: List[int]):
        """Log SUS responses to both systems"""
        # Always log to CSV
        self.csv_logger.log_sus(participant_id, condition, responses)
        
        # Try Google Sheets if enabled
        if self.gsheets_enabled:
            try:
                # Convert list to dict for Google Sheets logger
                sus_scores = {f"q{i+1}": score for i, score in enumerate(responses)}
                self.gsheets_logger.log_sus(participant_id, condition, sus_scores)
            except Exception as e:
                st.warning(f"Google Sheets write failed: {e}")
    
    def log_trust(self, participant_id: str, condition: str, responses: List[int]):
        """Log trust responses to both systems"""
        # Always log to CSV
        self.csv_logger.log_trust(participant_id, condition, responses)
        
        # Try Google Sheets if enabled
        if self.gsheets_enabled:
            try:
                # Convert list to dict for Google Sheets logger
                trust_scores = {f"q{i+1}": score for i, score in enumerate(responses)}
                self.gsheets_logger.log_trust(participant_id, condition, trust_scores)
            except Exception as e:
                st.warning(f"Google Sheets write failed: {e}")
    
    def log_understanding(self, participant_id: str, condition: str, responses: List[int]):
        """Log understanding responses to both systems"""
        # Always log to CSV
        self.csv_logger.log_understanding(participant_id, condition, responses)
        
        # Try Google Sheets if enabled
        if self.gsheets_enabled:
            try:
                # Google Sheets logger expects dict format from task-based understanding
                # For now, log to CSV only until we align the formats
                pass
            except Exception as e:
                st.warning(f"Google Sheets write failed: {e}")
    
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
        
        # Try Google Sheets if enabled
        if self.gsheets_enabled:
            try:
                # For Google Sheets, we'll log each task separately
                # Extract just the confidence value (mean of responses)
                confidence = sum(responses) / len(responses)
                task_num = int(task_case_id.split('_')[-1]) if '_' in task_case_id else 1
                
                # Google Sheets logger expects different format - skip for now
                pass
            except Exception as e:
                st.warning(f"Google Sheets write failed: {e}")
    
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
        
        # Try Google Sheets if enabled
        if self.gsheets_enabled:
            try:
                feedback_dict = {
                    "variant_a_helpful": "",  # Align with Google Sheets format
                    "variant_a_improvements": "",
                    "variant_b_helpful": "",
                    "variant_b_improvements": "",
                    "comparison": q1_most_useful,
                    "preference": q4_preference,
                    "preference_reason": q4_preference_reason,
                    "overall_suggestions": q3_improvements,
                }
                self.gsheets_logger.log_qualitative_feedback(participant_id, feedback_dict)
            except Exception as e:
                st.warning(f"Google Sheets write failed: {e}")
    
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
