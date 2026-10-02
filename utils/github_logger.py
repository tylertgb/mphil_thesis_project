"""
GitHub API Logger - Write to Separate Data Branch
─────────────────────────────────────────────────────────────────────────────
Writes participant responses directly to GitHub via REST API to avoid:
1. Streamlit Cloud file storage limitations
2. App restart loops (uses separate 'data' branch)
3. Need for external databases

Setup:
1. Create GitHub Personal Access Token (repo scope)
2. Add to Streamlit secrets: GITHUB_TOKEN = "ghp_..."
3. Create 'data' branch in your repo (or it will be auto-created)
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
import requests
import json
import base64
import pandas as pd
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Dict, List


class GitHubLogger:
    """
    Log study data to GitHub via REST API.
    
    Writes to separate 'data' branch to prevent Streamlit Cloud app restarts.
    """
    
    def __init__(self, repo: str = None, data_branch: str = "data"):
        """
        Initialize GitHub logger.
        
        Args:
            repo: GitHub repo in format "username/repo_name"
            data_branch: Branch name for data storage (default: "data")
        """
        # Get GitHub token from secrets
        if "GITHUB_TOKEN" not in st.secrets:
            st.warning("⚠️ GitHub token not found. Data will only be saved locally.")
            self.enabled = False
            return
        
        self.token = st.secrets["GITHUB_TOKEN"]
        self.repo = repo or st.secrets.get("GITHUB_REPO", "tylertgb/mphil_thesis_project")
        self.branch = data_branch
        self.base_url = f"https://api.github.com/repos/{self.repo}/contents"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.enabled = True
    
    def _get_file_content(self, file_path: str) -> tuple:
        """
        Fetch existing file content from GitHub.
        
        Returns:
            (content_str, sha) or (None, None) if file doesn't exist
        """
        url = f"{self.base_url}/{file_path}"
        params = {"ref": self.branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                file_json = response.json()
                content = base64.b64decode(file_json["content"]).decode("utf-8")
                return content, file_json["sha"]
            elif response.status_code == 404:
                return None, None
            else:
                st.error(f"GitHub API error: {response.json().get('message', 'Unknown error')}")
                return None, None
        except Exception as e:
            st.error(f"Failed to fetch from GitHub: {e}")
            return None, None
    
    def _push_file_content(self, file_path: str, content: str, sha: str = None) -> bool:
        """
        Push file content to GitHub.
        
        Args:
            file_path: Path within repo (e.g., "study_data/demographics.csv")
            content: File content as string
            sha: Existing file SHA (required for updates)
        
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/{file_path}"
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        
        payload = {
            "message": f"Update {file_path} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "content": encoded_content,
            "branch": self.branch
        }
        
        if sha:
            payload["sha"] = sha
        
        try:
            response = requests.put(url, headers=self.headers, data=json.dumps(payload), timeout=10)
            
            if response.status_code in [200, 201]:
                return True
            else:
                error_msg = response.json().get('message', 'Unknown error')
                st.error(f"Failed to commit to GitHub: {error_msg}")
                return False
        except Exception as e:
            st.error(f"GitHub push failed: {e}")
            return False
    
    def _append_to_csv(self, file_path: str, new_row: Dict) -> bool:
        """
        Append a row to a CSV file on GitHub.
        
        Args:
            file_path: Path to CSV file
            new_row: Dictionary with column:value pairs
        
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        # Get existing content
        existing_content, sha = self._get_file_content(file_path)
        
        if existing_content:
            # Append to existing file
            try:
                df = pd.read_csv(StringIO(existing_content))
                new_df = pd.DataFrame([new_row])
                updated_df = pd.concat([df, new_df], ignore_index=True)
            except Exception as e:
                st.error(f"Error reading existing CSV: {e}")
                return False
        else:
            # Create new file
            updated_df = pd.DataFrame([new_row])
        
        # Convert to CSV string
        csv_content = updated_df.to_csv(index=False)
        
        # Push to GitHub
        return self._push_file_content(file_path, csv_content, sha)
    
    def log_demographics(self, participant_id: str, demographics: Dict):
        """Log demographics data"""
        row = {
            "participant_id": participant_id,
            "age_group": demographics.get("age_group", ""),
            "gender": demographics.get("gender", ""),
            "education_level": demographics.get("education_level", ""),
            "role": demographics.get("role", ""),
            "years_experience": demographics.get("years_experience", ""),
            "familiarity_with_analytics": demographics.get("familiarity_with_analytics", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        return self._append_to_csv("study_data/demographics.csv", row)
    
    def log_sus(self, participant_id: str, condition: str, responses: List[int]):
        """Log SUS responses"""
        # Calculate SUS score
        score = 0
        for i, resp in enumerate(responses, 1):
            if i % 2 == 1:  # Odd items
                score += (resp - 1)
            else:  # Even items
                score += (5 - resp)
        sus_score = score * 2.5
        
        row = {
            "participant_id": participant_id,
            "condition": condition,
            **{f"item_{i}": responses[i-1] for i in range(1, 11)},
            "sus_score": sus_score,
            "timestamp": datetime.now().isoformat()
        }
        
        return self._append_to_csv("study_data/sus_responses.csv", row)
    
    def log_trust(self, participant_id: str, condition: str, responses: List[int]):
        """Log trust responses"""
        trust_mean = sum(responses) / len(responses)
        
        row = {
            "participant_id": participant_id,
            "condition": condition,
            **{f"trust_{i}": responses[i-1] for i in range(1, len(responses)+1)},
            "trust_mean": trust_mean,
            "timestamp": datetime.now().isoformat()
        }
        
        return self._append_to_csv("study_data/trust_responses.csv", row)
    
    def log_understanding(self, participant_id: str, condition: str, responses: List[int]):
        """Log understanding responses"""
        understanding_mean = sum(responses) / len(responses)
        
        row = {
            "participant_id": participant_id,
            "condition": condition,
            **{f"understanding_{i}": responses[i-1] for i in range(1, 6)},
            "understanding_mean": understanding_mean,
            "timestamp": datetime.now().isoformat()
        }
        
        return self._append_to_csv("study_data/understanding_responses.csv", row)
    
    def log_decision_confidence(
        self, 
        participant_id: str, 
        condition: str, 
        task_case_id: str, 
        responses: List[int]
    ):
        """Log decision confidence"""
        confidence_mean = sum(responses) / len(responses)
        
        row = {
            "participant_id": participant_id,
            "condition": condition,
            "task_case_id": task_case_id,
            **{f"confidence_{i}": responses[i-1] for i in range(1, 5)},
            "confidence_mean": confidence_mean,
            "timestamp": datetime.now().isoformat()
        }
        
        return self._append_to_csv("study_data/decision_confidence.csv", row)
    
    def log_qualitative_feedback(
        self,
        participant_id: str,
        q1_most_useful: str,
        q2_challenges: str,
        q3_improvements: str,
        q4_preference: str,
        q4_preference_reason: str,
    ):
        """Log qualitative feedback"""
        row = {
            "participant_id": participant_id,
            "q1_most_useful": q1_most_useful,
            "q2_challenges": q2_challenges,
            "q3_improvements": q3_improvements,
            "q4_preference": q4_preference,
            "q4_preference_reason": q4_preference_reason,
            "timestamp": datetime.now().isoformat()
        }
        
        return self._append_to_csv("study_data/qualitative_feedback.csv", row)
    
    def log_session(self, participant_id: str, variant: str, status: str = "active"):
        """
        Log active session to separate branch for cross-app session tracking.
        
        This allows Variant B to detect that Variant A was completed.
        """
        row = {
            "participant_id": participant_id,
            "variant": variant,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        return self._append_to_csv("study_data/active_sessions.csv", row)
