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
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class StudyResponseLogger:
    """
    Logs participant responses throughout the study.
    
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
        
        # Perceived Understanding (3-5 items, 1-5 Likert)
        if not self.understanding_file.exists():
            with open(self.understanding_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'participant_id',
                    'condition',
                    'understanding_1',  # I understand why the system made this prediction
                    'understanding_2',  # I could explain this prediction to someone else
                    'understanding_3',  # The explanation was clear and understandable
                    'understanding_mean',
                    'timestamp',
                ])
        
        # Decision Confidence (per task case)
        if not self.confidence_file.exists():
            with open(self.confidence_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'participant_id',
                    'condition',
                    'task_case_id',
                    'confidence',  # 1-5 scale: How confident are you in this prediction?
                    'agreement',   # 1-5 scale: How much do you agree with this prediction?
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
        with open(self.demographics_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                participant_id,
                demographics.get('age_group'),
                demographics.get('gender'),
                demographics.get('education_level'),
                demographics.get('role'),
                demographics.get('years_experience'),
                demographics.get('familiarity_with_analytics'),
                datetime.now().isoformat(),
            ])
    
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
        # Odd items: contribution = (response - 1)
        # Even items: contribution = (5 - response)
        # Score = sum(contributions) * 2.5
        score = 0
        for i, resp in enumerate(responses, 1):
            if i % 2 == 1:  # Odd items
                score += (resp - 1)
            else:  # Even items
                score += (5 - resp)
        sus_score = score * 2.5
        
        with open(self.sus_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                participant_id,
                condition,
                *responses,
                sus_score,
                datetime.now().isoformat(),
            ])
    
    def log_trust(self, participant_id: str, condition: str, responses: List[int]):
        """Log trust scale responses for a condition."""
        assert condition in ["variant_a", "variant_b"], f"Invalid condition: {condition}"
        
        trust_mean = sum(responses) / len(responses)
        
        with open(self.trust_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                participant_id,
                condition,
                *responses,
                trust_mean,
                datetime.now().isoformat(),
            ])
    
    def log_understanding(self, participant_id: str, condition: str, responses: List[int]):
        """Log perceived understanding responses for a condition."""
        assert condition in ["variant_a", "variant_b"], f"Invalid condition: {condition}"
        
        understanding_mean = sum(responses) / len(responses)
        
        with open(self.understanding_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                participant_id,
                condition,
                *responses,
                understanding_mean,
                datetime.now().isoformat(),
            ])
    
    def log_decision_confidence(
        self,
        participant_id: str,
        condition: str,
        task_case_id: str,
        confidence: int,
        agreement: int,
    ):
        """Log decision confidence for a specific task case."""
        assert condition in ["variant_a", "variant_b"], f"Invalid condition: {condition}"
        
        with open(self.confidence_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                participant_id,
                condition,
                task_case_id,
                confidence,
                agreement,
                datetime.now().isoformat(),
            ])
    
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
        
        Args:
            participant_id: Unique participant identifier
            q1_most_useful: What did you find most useful about the system?
            q2_challenges: What challenges did you experience while using the system?
            q3_improvements: How can the explanation interface be improved?
            q4_preference: Which interface did you prefer (Static / Progressive)?
            q4_preference_reason: Why did you prefer that interface?
        """
        with open(self.qualitative_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                participant_id,
                q1_most_useful,
                q2_challenges,
                q3_improvements,
                q4_preference,
                q4_preference_reason,
                datetime.now().isoformat(),
            ])
    
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
    
    # Collect understanding
    understanding_responses = [5, 4, 5]  # 3 items
    logger.log_understanding(participant_id, "variant_a", understanding_responses)
    
    # Log decision confidence for each task case
    for task_id in ["high_risk_1", "medium_risk_4", "low_risk_7"]:
        logger.log_decision_confidence(
            participant_id,
            "variant_a",
            task_id,
            confidence=4,  # 1-5
            agreement=4,   # 1-5
        )
    
    # 3. Participant uses Variant B
    # Repeat the same measures for Variant B
    sus_responses_b = [5, 1, 5, 1, 5, 1, 5, 1, 5, 1]
    logger.log_sus(participant_id, "variant_b", sus_responses_b)
    
    trust_responses_b = [5, 5, 5, 5, 5]
    logger.log_trust(participant_id, "variant_b", trust_responses_b)
    
    understanding_responses_b = [5, 5, 5]
    logger.log_understanding(participant_id, "variant_b", understanding_responses_b)
    
    for task_id in ["high_risk_1", "medium_risk_4", "low_risk_7"]:
        logger.log_decision_confidence(
            participant_id,
            "variant_b",
            task_id,
            confidence=5,
            agreement=5,
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
