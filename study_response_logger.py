"""
Study Response Logger
─────────────────────────────────────────────────────────────────────────────
MPhil Thesis: A Human-Centered Evaluation of SHAP-Based Explainable Interfaces
              for Logistic Regression Models in Educational Decision-Support Systems

Provides logging infrastructure for collecting participant responses during
the user study evaluation.

Captures:
- SUS (System Usability Scale) - 10 items per condition
- Trust Scale (adapted) - per condition
- Perceived Understanding - per condition  
- Decision Confidence - per task case per condition
- Demographics and background

Output: CSV files compatible with statistical analysis (paired t-tests, etc.)
─────────────────────────────────────────────────────────────────────────────
"""

import csv
import json
import fcntl
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class StudyResponseLogger:
    """
    Logs participant responses throughout the study.
    
    Thread-safe for concurrent users via file locking.
    
    Within-subjects design:
    - Each participant uses BOTH interfaces (A and B)
    - Order is counterbalanced across participants
    - Each interface is used with the same set of task cases
    """
    
    def __init__(self, output_dir: str = "study_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.demographics_file = self.output_dir / "demographics.csv"
        self.sus_file = self.output_dir / "sus_responses.csv"
        self.trust_file = self.output_dir / "trust_responses.csv"
        self.understanding_file = self.output_dir / "understanding_responses.csv"
        self.confidence_file = self.output_dir / "decision_confidence.csv"
        self.qualitative_file = self.output_dir / "qualitative_feedback.csv"
        self.metadata_file = self.output_dir / "session_metadata.json"
        
        self._initialize_files()
    
    def _write_with_lock(self, filepath: Path, row: List, mode='a'):
        """
        Thread-safe CSV write with file locking for concurrent users.
        
        Args:
            filepath: Path to CSV file
            row: List of values to write
            mode: File open mode ('a' for append, 'w' for write)
        """
        max_retries = 5
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                with open(filepath, mode, newline='', encoding='utf-8') as f:
                    # Acquire exclusive lock (Unix/Linux)
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except (IOError, AttributeError):
                        # fcntl not available on Windows, fall back to retry logic
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                    
                    writer = csv.writer(f)
                    writer.writerow(row)
                    
                    # Release lock (automatic on file close, but explicit is better)
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    except (IOError, AttributeError):
                        pass
                
                return  # Success
                
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"Failed to write to {filepath} after {max_retries} attempts: {e}")
    
    def _initialize_files(self):
        """Create CSV files with headers if they don't exist."""
        
        # Demographics
        if not self.demographics_file.exists():
            with open(self.demographics_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'participant_id',
                    'age_group',
                    'gender',
                    'education_level',
                    'role',  # e.g., tutor, academic advisor, admin staff
                    'years_experience',
                    'familiarity_with_analytics',  # 1-5 scale
                    'timestamp',
                ])
        
        # SUS (10 items, 1-5 Likert scale)
        if not self.sus_file.exists():
            with open(self.sus_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'participant_id',
                    'condition',  # variant_a or variant_b
                    'item_1',  # I think I would like to use this system frequently
                    'item_2',  # I found the system unnecessarily complex
                    'item_3',  # I thought the system was easy to use
                    'item_4',  # I think I would need support to use this system
                    'item_5',  # I found the various functions well integrated
                    'item_6',  # I thought there was too much inconsistency
                    'item_7',  # I would imagine most people would learn quickly
                    'item_8',  # I found the system very cumbersome
                    'item_9',  # I felt very confident using the system
                    'item_10', # I needed to learn a lot before I could get going
                    'sus_score',  # Computed SUS score (0-100)
                    'timestamp',
                ])
        
        # Trust Scale (adapted, 5-7 items, 1-5 Likert)
        if not self.trust_file.exists():
            with open(self.trust_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'participant_id',
                    'condition',
                    'trust_1',  # I would trust this system's predictions
                    'trust_2',  # The explanations helped me understand the predictions
                    'trust_3',  # I feel confident using this system for real decisions
                    'trust_4',  # The system provides sufficient information
                    'trust_5',  # I would be comfortable explaining this to a student
                    'trust_mean',  # Mean trust score
                    'timestamp',
                ])
        
        # Perceived Understanding (Section D: 5 items, 1-5 Likert)
        if not self.understanding_file.exists():
            with open(self.understanding_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'participant_id',
                    'condition',
                    'understanding_1',  # I understand how the system arrived at its prediction.
                    'understanding_2',  # The explanation provided by the system is clear and understandable.
                    'understanding_3',  # The explanation helped me interpret the prediction effectively.
                    'understanding_4',  # I can identify which factors influenced the prediction.
                    'understanding_5',  # The explanation improved my overall understanding of the system's output.
                    'understanding_mean',
                    'timestamp',
                ])
        
        # Decision Confidence (Section E: 4 items per task case, 1-5 Likert)
        if not self.confidence_file.exists():
            with open(self.confidence_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'participant_id',
                    'condition',
                    'task_case_id',
                    'confidence_1',  # I feel confident in the decision I made using the system.
                    'confidence_2',  # The system helped me make a more informed decision.
                    'confidence_3',  # I would be comfortable making similar decisions using this system in the future.
                    'confidence_4',  # The explanation increased my confidence in my decision.
                    'confidence_mean',
                    'timestamp',
                ])
        
        # Qualitative Feedback (Section F: Additional Feedback)
        if not self.qualitative_file.exists():
            with open(self.qualitative_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'participant_id',
                    'q1_most_useful',        # What did you find most useful?
                    'q2_challenges',         # What challenges did you experience?
                    'q3_improvements',       # How can the interface be improved?
                    'q4_preference',         # Which interface did you prefer?
                    'q4_preference_reason',  # Why?
                    'timestamp',
                ])
    
    def log_demographics(self, participant_id: str, demographics: Dict):
        """Log participant demographics at study start."""
        row = [
            participant_id,
            demographics.get('age_group'),
            demographics.get('gender'),
            demographics.get('education_level'),
            demographics.get('role'),
            demographics.get('years_experience'),
            demographics.get('familiarity_with_analytics'),
            datetime.now().isoformat(),
        ]
        self._write_with_lock(self.demographics_file, row)
    
    def log_sus(self, participant_id: str, condition: str, responses: List[int]):
        """
        Log SUS responses for a condition.
        
        Args:
            participant_id: Unique participant identifier
            condition: "variant_a" or "variant_b"
            responses: List of 10 integers (1-5 Likert responses)
        """
        assert len(responses) == 10, "SUS requires exactly 10 item responses"
        assert condition in ["variant_a", "variant_b"], f"Invalid condition: {condition}"
        
        # Compute SUS score (0-100)
        score = 0
        for i, resp in enumerate(responses, 1):
            if i % 2 == 1:  # Odd items
                score += (resp - 1)
            else:  # Even items
                score += (5 - resp)
        sus_score = score * 2.5
        
        row = [
            participant_id,
            condition,
            *responses,
            sus_score,
            datetime.now().isoformat(),
        ]
        self._write_with_lock(self.sus_file, row)
    
    def log_trust(self, participant_id: str, condition: str, responses: List[int]):
        """Log trust scale responses for a condition."""
        assert condition in ["variant_a", "variant_b"], f"Invalid condition: {condition}"
        
        trust_mean = sum(responses) / len(responses)
        
        row = [
            participant_id,
            condition,
            *responses,
            trust_mean,
            datetime.now().isoformat(),
        ]
        self._write_with_lock(self.trust_file, row)
    
    def log_understanding(self, participant_id: str, condition: str, responses: List[int]):
        """
        Log perceived understanding responses for a condition.
        
        Section D: Perceived Understanding (5 items, 1-5 Likert scale)
        """
        assert condition in ["variant_a", "variant_b"], f"Invalid condition: {condition}"
        assert len(responses) == 5, f"Expected 5 responses, got {len(responses)}"
        assert all(1 <= r <= 5 for r in responses), "All responses must be 1-5"
        
        understanding_mean = sum(responses) / len(responses)
        
        row = [
            participant_id,
            condition,
            *responses,
            understanding_mean,
            datetime.now().isoformat(),
        ]
        self._write_with_lock(self.understanding_file, row)
    
    def log_decision_confidence(
        self,
        participant_id: str,
        condition: str,
        task_case_id: str,
        responses: List[int],
    ):
        """
        Log decision confidence for a specific task case.
        
        Section E: Decision Confidence (4 items, 1-5 Likert scale)
        """
        assert condition in ["variant_a", "variant_b"], f"Invalid condition: {condition}"
        assert len(responses) == 4, f"Expected 4 responses, got {len(responses)}"
        assert all(1 <= r <= 5 for r in responses), "All responses must be 1-5"
        
        confidence_mean = sum(responses) / len(responses)
        
        row = [
            participant_id,
            condition,
            task_case_id,
            *responses,
            confidence_mean,
            datetime.now().isoformat(),
        ]
        self._write_with_lock(self.confidence_file, row)
    
    def log_qualitative_feedback(
        self,
        participant_id: str,
        q1_most_useful: str,
        q2_challenges: str,
        q3_improvements: str,
        q4_preference: str,
        q4_preference_reason: str,
    ):
        """
        Log qualitative feedback responses (Section F: Additional Feedback).
        
        These are asked ONCE at the end of the session, after both conditions.
        """
        row = [
            participant_id,
            q1_most_useful,
            q2_challenges,
            q3_improvements,
            q4_preference,
            q4_preference_reason,
            datetime.now().isoformat(),
        ]
        self._write_with_lock(self.qualitative_file, row)
    
    def log_session_metadata(
        self,
        participant_id: str,
        order: str,  # "A_then_B" or "B_then_A"
        duration_minutes: Optional[int] = None,
        task_cases_shown: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ):
        """
        Log session-level metadata.
        
        Args:
            participant_id: Unique participant identifier
            order: Condition order for counterbalancing ("A_then_B" or "B_then_A")
            duration_minutes: Total session duration
            task_cases_shown: List of task case IDs shown in order
            notes: Optional session notes
        """
        metadata = {
            "participant_id": participant_id,
            "condition_order": order,
            "duration_minutes": duration_minutes,
            "task_cases_shown": task_cases_shown,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Append to metadata file (JSONL format)
        with open(self.metadata_file, 'a') as f:
            f.write(json.dumps(metadata) + '\n')


# ── Example Usage ──────────────────────────────────────────────────────────────


def example_usage():
    """Demonstrate how to use the logger during a study session."""
    logger = StudyResponseLogger(output_dir="study_data")
    
    participant_id = "P001"
    
    # 1. Log demographics at start
    logger.log_demographics(participant_id, {
        'age_group': '30-39',
        'gender': 'Female',
        'education_level': 'Masters',
        'role': 'Academic Tutor',
        'years_experience': 5,
        'familiarity_with_analytics': 3,  # 1-5 scale
    })
    
    # 2. Participant uses Variant A first
    # After completing task cases with Variant A, collect SUS
    sus_responses = [4, 2, 5, 2, 4, 1, 4, 2, 5, 1]  # 10 items, 1-5 Likert
    logger.log_sus(participant_id, "variant_a", sus_responses)
    
    # Collect trust
    trust_responses = [4, 5, 4, 5, 4]  # 5 items
    logger.log_trust(participant_id, "variant_a", trust_responses)
    
    # Collect understanding (5 items)
    understanding_responses = [5, 4, 5, 4, 5]  # Section D: 5 items
    logger.log_understanding(participant_id, "variant_a", understanding_responses)
    
    # Log decision confidence for each task case (4 items per case)
    for task_id in ["high_risk_1", "medium_risk_4", "low_risk_7"]:
        confidence_responses = [4, 4, 3, 4]  # Section E: 4 items
        logger.log_decision_confidence(
            participant_id,
            "variant_a",
            task_id,
            confidence_responses,
        )
    
    # 3. Participant uses Variant B
    # Repeat the same measures for Variant B
    sus_responses_b = [5, 1, 5, 1, 5, 1, 5, 1, 5, 1]
    logger.log_sus(participant_id, "variant_b", sus_responses_b)
    
    trust_responses_b = [5, 5, 5, 5, 5]
    logger.log_trust(participant_id, "variant_b", trust_responses_b)
    
    understanding_responses_b = [5, 5, 5, 4, 5]  # 5 items
    logger.log_understanding(participant_id, "variant_b", understanding_responses_b)
    
    for task_id in ["high_risk_1", "medium_risk_4", "low_risk_7"]:
        confidence_responses_b = [5, 5, 4, 5]  # 4 items
        logger.log_decision_confidence(
            participant_id,
            "variant_b",
            task_id,
            confidence_responses_b,
        )
    
    # 4. Log session metadata at end
    logger.log_session_metadata(
        participant_id,
        order="A_then_B",
        duration_minutes=45,
        notes="Participant found both interfaces helpful but preferred B"
    )
    
    # 5. Log qualitative feedback (Section F - asked once at end)
    logger.log_qualitative_feedback(
        participant_id,
        q1_most_useful="The visual explanations helped me understand why the system made each prediction",
        q2_challenges="Some technical terms were unclear, needed more context",
        q3_improvements="Add tooltips for technical features like 'days_since_last_activity'",
        q4_preference="Progressive",
        q4_preference_reason="I liked seeing the summary first, then details if I needed them"
    )
    
    print("✓ Example session logged successfully")
    print(f"  Data saved to: study_data/")


# ── Data Analysis Helper ───────────────────────────────────────────────────────


def export_for_analysis(output_dir: str = "study_data", analysis_file: str = "study_data_for_analysis.csv"):
    """
    Merge all response files into a single wide-format CSV for statistical analysis.
    
    Each row = one participant, with columns for:
    - Demographics
    - Variant A: SUS, Trust, Understanding, mean Confidence
    - Variant B: SUS, Trust, Understanding, mean Confidence
    - Order (A_then_B or B_then_A)
    
    This format is suitable for paired t-tests in SPSS, R, or Python.
    """
    import pandas as pd
    
    output_dir = Path(output_dir)
    
    # Load all data
    demographics = pd.read_csv(output_dir / "demographics.csv")
    sus = pd.read_csv(output_dir / "sus_responses.csv")
    trust = pd.read_csv(output_dir / "trust_responses.csv")
    understanding = pd.read_csv(output_dir / "understanding_responses.csv")
    confidence = pd.read_csv(output_dir / "decision_confidence.csv")
    
    # Pivot confidence to get mean per participant per condition
    confidence_mean = confidence.groupby(['participant_id', 'condition'])['confidence'].mean().reset_index()
    confidence_mean = confidence_mean.pivot(index='participant_id', columns='condition', values='confidence')
    confidence_mean.columns = [f'decision_confidence_{col}' for col in confidence_mean.columns]  # Match hypothesis test script
    
    # Pivot other measures
    sus_wide = sus[['participant_id', 'condition', 'sus_score']].pivot(
        index='participant_id', columns='condition', values='sus_score'
    )
    sus_wide.columns = [f'sus_{col}' for col in sus_wide.columns]
    
    trust_wide = trust[['participant_id', 'condition', 'trust_mean']].pivot(
        index='participant_id', columns='condition', values='trust_mean'
    )
    trust_wide.columns = [f'trust_{col}' for col in trust_wide.columns]
    
    understanding_wide = understanding[['participant_id', 'condition', 'understanding_mean']].pivot(
        index='participant_id', columns='condition', values='understanding_mean'
    )
    understanding_wide.columns = [f'understanding_{col}' for col in understanding_wide.columns]
    
    # Merge everything
    merged = demographics[['participant_id', 'role', 'years_experience', 'familiarity_with_analytics']]
    merged = merged.merge(sus_wide, on='participant_id', how='left')
    merged = merged.merge(trust_wide, on='participant_id', how='left')
    merged = merged.merge(understanding_wide, on='participant_id', how='left')
    merged = merged.merge(confidence_mean, on='participant_id', how='left')
    
    # Save
    merged.to_csv(output_dir / analysis_file, index=False)
    print(f"✓ Analysis-ready data exported to {output_dir / analysis_file}")
    print(f"  Shape: {merged.shape[0]} participants × {merged.shape[1]} variables")
    print(f"\nReady for paired t-tests:")
    print(f"  - SUS: variant_a vs variant_b")
    print(f"  - Trust: variant_a vs variant_b")
    print(f"  - Understanding: variant_a vs variant_b")
    print(f"  - Decision Confidence: variant_a vs variant_b")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("STUDY RESPONSE LOGGER - EXAMPLE USAGE")
    print("=" * 80 + "\n")
    
    example_usage()
    
    print("\n" + "=" * 80)
    print("To use in your study:")
    print("  1. Create logger: logger = StudyResponseLogger('study_data')")
    print("  2. Log demographics at start of each session")
    print("  3. After each condition, log SUS, trust, understanding")
    print("  4. During tasks, log decision confidence per case")
    print("  5. At end, log session metadata")
    print("  6. After data collection, run export_for_analysis()")
    print("=" * 80 + "\n")
