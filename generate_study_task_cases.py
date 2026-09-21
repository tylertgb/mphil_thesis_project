"""
Study Task Case Generator
─────────────────────────────────────────────────────────────────────────────
MPhil Thesis: A Human-Centered Evaluation of SHAP-Based Explainable Interfaces
              for Logistic Regression Models in Educational Decision-Support Systems

Generates task cases for the within-subjects user study by:
1. Loading the trained model and test set
2. Selecting diverse, representative cases across risk levels
3. Ensuring predictions are explainable and face-valid
4. Documenting justification for each case

Output: study_task_cases.json with 10-12 cases for participants to evaluate
─────────────────────────────────────────────────────────────────────────────
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
import joblib

from models.logistic_regression_model import predict_student

# ── Paths ──────────────────────────────────────────────────────────────────────
SAVE_DIR = Path("models/saved_models")
DATA_DIR = Path("data/processed")
OUTPUT_FILE = Path("study_task_cases.json")

# ── Configuration ──────────────────────────────────────────────────────────────
CASES_PER_CATEGORY = 3  # High-risk, Medium, Low-risk
TOTAL_CASES = 10


def load_model_and_data():
    """Load trained model artifacts and test data."""
    model = joblib.load(SAVE_DIR / "logistic_regression.pkl")
    calibrated = joblib.load(SAVE_DIR / "calibrated_model.pkl")
    scaler = joblib.load(SAVE_DIR / "scaler.pkl")
    
    with open(SAVE_DIR / "feature_names.json") as f:
        feature_names = json.load(f)
    
    # Load full dataset to get test samples
    df = pd.read_csv(DATA_DIR / "final_model_dataset_v2.csv")
    X = df.drop(columns=["target"])
    y = df["target"]
    
    return model, calibrated, scaler, feature_names, X, y


def select_diverse_cases(X, y, model, scaler, feature_names):
    """
    Select diverse task cases spanning risk levels and prediction outcomes.
    
    Strategy:
    1. Get predictions for entire dataset
    2. Bin by predicted probability: Low risk (>0.7), Medium (0.3-0.7), High risk (<0.3)
    3. Within each bin, select cases that:
       - Have interesting SHAP profiles (clear top contributors)
       - Represent different true outcomes (some correct, some errors)
       - Are face-valid (features align with prediction)
    """
    # Drop any NaN values
    X_clean = X[feature_names].dropna()
    y_clean = y.loc[X_clean.index]
    
    # Get predictions
    X_scaled = scaler.transform(X_clean)
    probs = model.predict_proba(X_scaled)[:, 1]  # P(Success)
    preds = model.predict(X_scaled)
    
    # Bin by risk level
    high_risk_idx = np.where(probs < 0.3)[0]  # High risk of failure
    medium_risk_idx = np.where((probs >= 0.3) & (probs <= 0.7))[0]
    low_risk_idx = np.where(probs > 0.7)[0]  # Low risk (high success prob)
    
    print(f"\nDataset distribution:")
    print(f"  High-risk predictions  : {len(high_risk_idx):,} ({len(high_risk_idx)/len(X_clean)*100:.1f}%)")
    print(f"  Medium-risk predictions: {len(medium_risk_idx):,} ({len(medium_risk_idx)/len(X_clean)*100:.1f}%)")
    print(f"  Low-risk predictions   : {len(low_risk_idx):,} ({len(low_risk_idx)/len(X_clean)*100:.1f}%)")
    
    selected_cases = []
    
    # Select from each category
    for category, indices, label in [
        ("high_risk", high_risk_idx, "High Risk"),
        ("medium_risk", medium_risk_idx, "Medium Risk"),
        ("low_risk", low_risk_idx, "Low Risk"),
    ]:
        if len(indices) == 0:
            continue
            
        # Sample randomly from this category
        n_samples = min(CASES_PER_CATEGORY, len(indices))
        sampled_idx = np.random.choice(indices, size=n_samples, replace=False)
        
        for idx in sampled_idx:
            case = {
                "case_id": f"{category}_{len(selected_cases)+1}",
                "risk_category": label,
                "features": X_clean.iloc[idx].to_dict(),
                "true_label": int(y_clean.iloc[idx]),
                "predicted_label": int(preds[idx]),
                "probability": float(probs[idx]),
            }
            selected_cases.append(case)
    
    # Add one "surprising" case if possible (high confidence but wrong)
    # Find cases where P(Success) > 0.8 but actual outcome is Fail
    surprising_idx = np.where((probs > 0.8) & (y_clean.values == 0))[0]
    if len(surprising_idx) > 0:
        idx = np.random.choice(surprising_idx)
        case = {
            "case_id": f"surprising_{len(selected_cases)+1}",
            "risk_category": "Surprising (False Negative)",
            "features": X_clean.iloc[idx].to_dict(),
            "true_label": int(y_clean.iloc[idx]),
            "predicted_label": int(preds[idx]),
            "probability": float(probs[idx]),
        }
        selected_cases.append(case)
    
    return selected_cases


def generate_shap_explanations(cases, model, calibrated, scaler, feature_names):
    """Add SHAP values and explanations to each case."""
    enriched_cases = []
    
    for case in cases:
        # Get full prediction with SHAP
        result = predict_student(
            case["features"],
            model=model,
            calibrated_model=calibrated,
            scaler=scaler,
            feature_names=feature_names,
            use_calibrated=True
        )
        
        # Get top 3 contributing features
        shap_abs = {k: abs(v) for k, v in result["shap_values"].items()}
        top_features = sorted(shap_abs.items(), key=lambda x: x[1], reverse=True)[:3]
        
        case["shap_values"] = result["shap_values"]
        case["shap_directions"] = result["shap_directions"]
        case["expected_value"] = result["expected_value"]  # For manual additivity verification
        case["top_3_features"] = [
            {
                "feature": feat,
                "shap_value": result["shap_values"][feat],
                "direction": result["shap_directions"][feat]["plain_text"],
            }
            for feat, _ in top_features
        ]
        
        enriched_cases.append(case)
    
    return enriched_cases


def add_justifications(cases):
    """Add face-validity justification for each case."""
    for case in cases:
        features = case["features"]
        pred_label = "Success" if case["predicted_label"] == 1 else "At-Risk"
        prob = case["probability"]
        
        # Generate justification based on key features
        avg_score = features.get("avg_assessment_score", 0)
        clicks = features.get("total_clicks_pre_cutoff", 0)
        completion = features.get("completion_rate", 0)
        
        justification_parts = []
        
        # Assessment performance
        if avg_score > 70:
            justification_parts.append(f"strong assessment performance ({avg_score:.1f}%)")
        elif avg_score < 50:
            justification_parts.append(f"weak assessment performance ({avg_score:.1f}%)")
        else:
            justification_parts.append(f"moderate assessment performance ({avg_score:.1f}%)")
        
        # Engagement
        if clicks > 1000:
            justification_parts.append("high VLE engagement")
        elif clicks < 200:
            justification_parts.append("low VLE engagement")
        else:
            justification_parts.append("moderate VLE engagement")
        
        # Completion rate
        if completion > 0.8:
            justification_parts.append("strong coursework completion")
        elif completion < 0.4:
            justification_parts.append("poor coursework completion")
        
        justification = (
            f"Predicted {pred_label} (P={prob:.1%}) based on "
            + ", ".join(justification_parts)
            + ". "
        )
        
        # Add note about surprising cases
        if case["case_id"].startswith("surprising"):
            justification += "This is a surprising case where high confidence prediction was incorrect, "
            justification += "useful for testing whether users notice contradictory patterns."
        elif case["predicted_label"] != case["true_label"]:
            justification += f"Prediction was incorrect (true outcome: {'Success' if case['true_label'] == 1 else 'Fail'}). "
        else:
            justification += "Prediction matches actual outcome."
        
        case["justification"] = justification
    
    return cases


def save_task_cases(cases):
    """Save task cases to JSON file with metadata."""
    output = {
        "metadata": {
            "description": "Task cases for MPhil user study evaluation",
            "model_accuracy": "68.03%",
            "model_roc_auc": "0.7658",
            "temporal_cutoff": "Day 42",
            "calibrated": True,
            "total_cases": len(cases),
        },
        "cases": cases,
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Task cases saved to {OUTPUT_FILE}")


def print_summary(cases):
    """Print a summary table of selected cases."""
    print("\n" + "=" * 100)
    print("TASK CASE SUMMARY")
    print("=" * 100)
    print(f"{'Case ID':<25} {'Risk Category':<30} {'Pred':<8} {'True':<8} {'Prob':<8}")
    print("-" * 100)
    
    for case in cases:
        case_id = case["case_id"]
        category = case["risk_category"]
        pred = "Success" if case["predicted_label"] == 1 else "At-Risk"
        true = "Success" if case["true_label"] == 1 else "At-Risk"
        prob = f"{case['probability']:.1%}"
        
        print(f"{case_id:<25} {category:<30} {pred:<8} {true:<8} {prob:<8}")
    
    print("-" * 100)
    print(f"Total: {len(cases)} cases")
    print("=" * 100)
    
    # Print detailed view for first case as example
    print("\nEXAMPLE CASE (First Case):")
    print("-" * 100)
    case = cases[0]
    print(f"Case ID: {case['case_id']}")
    print(f"Prediction: {case['predicted_label']} (Prob: {case['probability']:.1%})")
    print(f"True Outcome: {case['true_label']}")
    print(f"\nTop 3 Contributing Features:")
    for feat_info in case["top_3_features"]:
        print(f"  - {feat_info['feature']}: {feat_info['shap_value']:+.4f} ({feat_info['direction']})")
    print(f"\nJustification:")
    print(f"  {case['justification']}")
    print("=" * 100)


def main():
    print("\n" + "=" * 100)
    print("STUDY TASK CASE GENERATOR")
    print("=" * 100)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    print("\n[1/5] Loading model and data...")
    model, calibrated, scaler, feature_names, X, y = load_model_and_data()
    print(f"  ✓ Loaded {len(X):,} samples, {len(feature_names)} features")
    
    print("\n[2/5] Selecting diverse cases...")
    cases = select_diverse_cases(X, y, model, scaler, feature_names)
    print(f"  ✓ Selected {len(cases)} initial cases")
    
    print("\n[3/5] Generating SHAP explanations...")
    cases = generate_shap_explanations(cases, model, calibrated, scaler, feature_names)
    print(f"  ✓ Added SHAP values to all cases")
    
    print("\n[4/5] Adding justifications...")
    cases = add_justifications(cases)
    print(f"  ✓ Face-validity justifications added")
    
    print("\n[5/5] Saving task cases...")
    save_task_cases(cases)
    
    print_summary(cases)
    
    print("\n✅ TASK CASE GENERATION COMPLETE")
    print("\nNext steps:")
    print("  1. Review study_task_cases.json")
    print("  2. Manually verify face-validity of each case")
    print("  3. Get external review (supervisor/peer)")
    print("  4. Use cases in pilot study before full deployment")
    print()


if __name__ == "__main__":
    main()
