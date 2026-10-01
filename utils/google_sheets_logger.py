"""
Google Sheets Logger
─────────────────────────────────────────────────────────────────────────────
Logs study responses to Google Sheets for real-time cloud data collection.

Setup Instructions:
1. Go to https://console.cloud.google.com/
2. Create new project (or use existing)
3. Enable Google Sheets API
4. Create Service Account → Download JSON key
5. Share Google Sheet with service account email
6. Add JSON key content to Streamlit secrets
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False


class GoogleSheetsLogger:
    """Log study data to Google Sheets"""
    
    def __init__(self):
        """Initialize Google Sheets connection"""
        if not GSHEETS_AVAILABLE:
            st.error("⚠️ gspread library not installed. Run: pip install gspread")
            self.client = None
            return
        
        # Check if running on Streamlit Cloud with secrets
        if "gcp_service_account" in st.secrets:
            # Use Streamlit secrets (cloud deployment)
            credentials = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
            self.client = gspread.authorize(credentials)
            self.spreadsheet_key = st.secrets.get("spreadsheet_key", "")
        else:
            # Local development - use service account JSON file
            try:
                credentials = Credentials.from_service_account_file(
                    "service_account.json",
                    scopes=[
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"
                    ]
                )
                self.client = gspread.authorize(credentials)
                # Read spreadsheet key from local config
                import json
                with open("google_sheets_config.json", "r") as f:
                    config = json.load(f)
                    self.spreadsheet_key = config["spreadsheet_key"]
            except FileNotFoundError:
                st.warning("⚠️ No Google Sheets credentials found. Using local CSV fallback.")
                self.client = None
    
    def _get_worksheet(self, sheet_name: str):
        """Get or create worksheet"""
        if not self.client or not self.spreadsheet_key:
            return None
        
        try:
            spreadsheet = self.client.open_by_key(self.spreadsheet_key)
            
            # Try to get existing worksheet
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                # Create new worksheet
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            
            return worksheet
        except Exception as e:
            st.error(f"Error accessing Google Sheets: {e}")
            return None
    
    def _append_row(self, sheet_name: str, row_data: List[Any], headers: List[str] = None):
        """Append a row to worksheet"""
        worksheet = self._get_worksheet(sheet_name)
        
        if not worksheet:
            return False
        
        try:
            # Check if headers exist
            existing_values = worksheet.get_all_values()
            if not existing_values:
                # Add headers if provided
                if headers:
                    worksheet.append_row(headers)
            
            # Append data row
            worksheet.append_row(row_data)
            return True
        except Exception as e:
            st.error(f"Error writing to Google Sheets: {e}")
            return False
    
    def log_demographics(self, participant_id: str, demographics: Dict[str, Any]):
        """Log demographic data"""
        headers = [
            "participant_id", "age_group", "gender", "education_level", 
            "role", "years_experience", "familiarity_with_analytics", "timestamp"
        ]
        
        row = [
            participant_id,
            demographics.get("age_group", ""),
            demographics.get("gender", ""),
            demographics.get("education_level", ""),
            demographics.get("role", ""),
            demographics.get("years_experience", ""),
            demographics.get("familiarity_with_analytics", ""),
            datetime.now().isoformat()
        ]
        
        return self._append_row("demographics", row, headers)
    
    def log_sus(self, participant_id: str, variant: str, sus_scores: Dict[str, int]):
        """Log SUS questionnaire responses"""
        headers = ["participant_id", "variant"] + [f"q{i}" for i in range(1, 11)] + ["timestamp"]
        
        row = [participant_id, variant] + [sus_scores.get(f"q{i}", 0) for i in range(1, 11)] + [datetime.now().isoformat()]
        
        return self._append_row("sus_responses", row, headers)
    
    def log_trust(self, participant_id: str, variant: str, trust_scores: Dict[str, int]):
        """Log trust questionnaire responses"""
        headers = ["participant_id", "variant"] + [f"q{i}" for i in range(1, 13)] + ["timestamp"]
        
        row = [participant_id, variant] + [trust_scores.get(f"q{i}", 0) for i in range(1, 13)] + [datetime.now().isoformat()]
        
        return self._append_row("trust_responses", row, headers)
    
    def log_understanding(self, participant_id: str, variant: str, understanding: Dict[str, Any]):
        """Log understanding assessment responses"""
        headers = [
            "participant_id", "variant", "task_number",
            "predicted_outcome", "actual_outcome", "match",
            "confidence", "timestamp"
        ]
        
        rows = []
        for task_num, task_data in understanding.items():
            if task_num.startswith("task_"):
                row = [
                    participant_id,
                    variant,
                    task_num.replace("task_", ""),
                    task_data.get("predicted_outcome", ""),
                    task_data.get("actual_outcome", ""),
                    task_data.get("match", False),
                    task_data.get("confidence", 0),
                    datetime.now().isoformat()
                ]
                rows.append(row)
        
        # Append all task rows
        worksheet = self._get_worksheet("understanding_responses")
        if not worksheet:
            return False
        
        try:
            # Check if headers exist
            existing_values = worksheet.get_all_values()
            if not existing_values:
                worksheet.append_row(headers)
            
            # Append all rows at once
            for row in rows:
                worksheet.append_row(row)
            
            return True
        except Exception as e:
            st.error(f"Error writing understanding data: {e}")
            return False
    
    def log_decision_confidence(self, participant_id: str, variant: str, task_number: int, 
                                predicted: str, confidence: int):
        """Log decision confidence for a task"""
        headers = [
            "participant_id", "variant", "task_number",
            "predicted_outcome", "confidence", "timestamp"
        ]
        
        row = [
            participant_id,
            variant,
            task_number,
            predicted,
            confidence,
            datetime.now().isoformat()
        ]
        
        return self._append_row("decision_confidence", row, headers)
    
    def log_qualitative_feedback(self, participant_id: str, feedback: Dict[str, str]):
        """Log qualitative feedback"""
        headers = [
            "participant_id", "variant_a_helpful", "variant_a_improvements",
            "variant_b_helpful", "variant_b_improvements",
            "comparison", "preference", "preference_reason",
            "overall_suggestions", "timestamp"
        ]
        
        row = [
            participant_id,
            feedback.get("variant_a_helpful", ""),
            feedback.get("variant_a_improvements", ""),
            feedback.get("variant_b_helpful", ""),
            feedback.get("variant_b_improvements", ""),
            feedback.get("comparison", ""),
            feedback.get("preference", ""),
            feedback.get("preference_reason", ""),
            feedback.get("overall_suggestions", ""),
            datetime.now().isoformat()
        ]
        
        return self._append_row("qualitative_feedback", row, headers)
