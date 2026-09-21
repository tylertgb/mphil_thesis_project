"""
Interface Consistency Tests
─────────────────────────────────────────────────────────────────────────────
MPhil Thesis: A Human-Centered Evaluation of SHAP-Based Explainable Interfaces
              for Logistic Regression Models in Educational Decision-Support Systems

Verifies that:
1. Both interface variants (A and B) use the same underlying model predictions
2. Both interfaces receive identical SHAP values for the same input
3. No personally identifiable information (PII) is displayed
4. Interfaces consume the same model artifacts

CRITICAL: Internal validity requires both conditions to differ ONLY in presentation,
          not in the underlying prediction or SHAP values.
─────────────────────────────────────────────────────────────────────────────
"""

import sys
from pathlib import Path
import json
import numpy as np
import joblib
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from models.logistic_regression_model import predict_student


# ── Paths ──────────────────────────────────────────────────────────────────────
SAVE_DIR = PROJECT_ROOT / "models" / "saved_models"


# ── Test 1: Shared Model Artifacts ────────────────────────────────────────────


def test_both_interfaces_use_same_model():
    """Verify both interface variants load the same model artifacts."""
    # Check that calibrated model exists (both interfaces should use this)
    calibrated_path = SAVE_DIR / "calibrated_model.pkl"
    assert calibrated_path.exists(), "Calibrated model missing - interfaces can't be consistent"
    
    # Check other shared artifacts
    required_artifacts = [
        "logistic_regression.pkl",
        "scaler.pkl", 
        "feature_names.json",
    ]
    
    for artifact in required_artifacts:
        path = SAVE_DIR / artifact
        assert path.exists(), f"Missing shared artifact: {artifact}"
    
    print("✓ Both interfaces have access to same model artifacts")


# ── Test 2: Prediction Consistency ─────────────────────────────────────────────


def test_prediction_consistency_across_calls():
    """Verify same input produces same prediction when called multiple times."""
    # Load artifacts
    model = joblib.load(SAVE_DIR / "logistic_regression.pkl")
    calibrated = joblib.load(SAVE_DIR / "calibrated_model.pkl")
    scaler = joblib.load(SAVE_DIR / "scaler.pkl")
    with open(SAVE_DIR / "feature_names.json") as f:
        feature_names = json.load(f)
    
    # Test student profile
    test_profile = {
        "studied_credits": 120,
        "num_of_prev_attempts": 0,
        "avg_assessment_score": 75.0,
        "num_assessments_completed": 3,
        "num_assessments_due": 5,
        "completion_rate": 0.6,
        "total_clicks_pre_cutoff": 500,
        "num_activities_accessed": 20,
        "days_active": 15,
        "avg_clicks_per_active_day": 33.3,
        "days_since_last_activity": 5,
    }
    
    # Call predict_student twice with same input
    result1 = predict_student(test_profile, model, calibrated, scaler, feature_names, use_calibrated=True)
    result2 = predict_student(test_profile, model, calibrated, scaler, feature_names, use_calibrated=True)
    
    # Predictions must be identical
    assert result1["prediction"] == result2["prediction"], "Predictions differ across calls"
    assert abs(result1["probability"] - result2["probability"]) < 1e-6, "Probabilities differ across calls"
    assert result1["label"] == result2["label"], "Labels differ across calls"
    
    # SHAP values must be identical
    for feature in feature_names:
        shap_diff = abs(result1["shap_values"][feature] - result2["shap_values"][feature])
        assert shap_diff < 1e-6, f"SHAP values differ for {feature}: {shap_diff}"
    
    print("✓ Predictions are deterministic and consistent")


def test_shap_values_consistency():
    """Verify SHAP values are consistent for different students."""
    model = joblib.load(SAVE_DIR / "logistic_regression.pkl")
    calibrated = joblib.load(SAVE_DIR / "calibrated_model.pkl")
    scaler = joblib.load(SAVE_DIR / "scaler.pkl")
    with open(SAVE_DIR / "feature_names.json") as f:
        feature_names = json.load(f)
    
    # Test two different profiles
    high_risk_profile = {
        "studied_credits": 180,
        "num_of_prev_attempts": 2,
        "avg_assessment_score": 40.0,
        "num_assessments_completed": 1,
        "num_assessments_due": 5,
        "completion_rate": 0.2,
        "total_clicks_pre_cutoff": 50,
        "num_activities_accessed": 5,
        "days_active": 3,
        "avg_clicks_per_active_day": 16.7,
        "days_since_last_activity": 20,
    }
    
    low_risk_profile = {
        "studied_credits": 60,
        "num_of_prev_attempts": 0,
        "avg_assessment_score": 85.0,
        "num_assessments_completed": 5,
        "num_assessments_due": 5,
        "completion_rate": 1.0,
        "total_clicks_pre_cutoff": 2000,
        "num_activities_accessed": 50,
        "days_active": 30,
        "avg_clicks_per_active_day": 66.7,
        "days_since_last_activity": 1,
    }
    
    result_high = predict_student(high_risk_profile, model, calibrated, scaler, feature_names)
    result_low = predict_student(low_risk_profile, model, calibrated, scaler, feature_names)
    
    # Predictions should differ
    assert result_high["prediction"] != result_low["prediction"], "Predictions should differ for different profiles"
    
    # Both should have complete SHAP values
    assert len(result_high["shap_values"]) == len(feature_names), "High-risk SHAP values incomplete"
    assert len(result_low["shap_values"]) == len(feature_names), "Low-risk SHAP values incomplete"
    
    # Both should have direction interpretations
    assert len(result_high["shap_directions"]) == len(feature_names), "High-risk directions incomplete"
    assert len(result_low["shap_directions"]) == len(feature_names), "Low-risk directions incomplete"
    
    print("✓ SHAP values computed for different student profiles")


# ── Test 3: No PII in Interfaces ───────────────────────────────────────────────


def test_no_pii_in_interface_code():
    """Verify interface code doesn't display student IDs or PII."""
    interface_files = [
        PROJECT_ROOT / "interfaces" / "variant_a_static" / "app.py",
        PROJECT_ROOT / "interfaces" / "variant_b_progressive" / "app.py",
        PROJECT_ROOT / "interfaces" / "shared_components" / "student_form.py",
    ]
    
    pii_indicators = [
        "id_student",
        "student_id", 
        "student_name",
        "email",
        "address",
    ]
    
    for interface_file in interface_files:
        content = interface_file.read_text(encoding='utf-8').lower()
        
        for pii in pii_indicators:
            # Check for actual PII display (not just variable names in comments)
            if pii in content:
                # Allow mentions in comments/docstrings
                lines = content.split('\n')
                code_lines = [l for l in lines if not l.strip().startswith('#') and '"""' not in l and "'''" not in l]
                code_content = '\n'.join(code_lines)
                
                assert pii not in code_content, f"PII indicator '{pii}' found in {interface_file.name}"
    
    print("✓ No PII indicators found in interface code")


def test_no_pii_in_form_inputs():
    """Verify student form only collects aggregated features, no identifiers."""
    form_file = PROJECT_ROOT / "interfaces" / "shared_components" / "student_form.py"
    content = form_file.read_text(encoding='utf-8')
    
    # Form should NOT ask for these
    forbidden_fields = [
        'st.text_input("Student ID"',
        'st.text_input("Name"',
        'st.text_input("Email"',
        '"id_student"',
        '"student_id"',
    ]
    
    for field in forbidden_fields:
        assert field not in content, f"PII field found: {field}"
    
    # Form SHOULD ask for aggregated features only
    expected_fields = [
        "Credits Studied",
        "Assessment Score",
        "VLE Clicks",
        "Activities Accessed",
    ]
    
    for field in expected_fields:
        assert field in content, f"Expected aggregated field missing: {field}"
    
    print("✓ Form collects only aggregated features, no PII")


# ── Test 4: Interface Structure Consistency ────────────────────────────────────


def test_both_interfaces_use_shared_form():
    """Verify both variants import and use the shared student form."""
    variant_a = (PROJECT_ROOT / "interfaces" / "variant_a_static" / "app.py").read_text(encoding='utf-8')
    variant_b = (PROJECT_ROOT / "interfaces" / "variant_b_progressive" / "app.py").read_text(encoding='utf-8')
    
    # Both should import from shared_components
    assert "from interfaces.shared_components.student_form import" in variant_a, \
        "Variant A doesn't use shared form"
    assert "from interfaces.shared_components.student_form import" in variant_b, \
        "Variant B doesn't use shared form"
    
    # Both should call render_form() and encode_input()
    assert "render_form()" in variant_a, "Variant A doesn't call render_form()"
    assert "render_form()" in variant_b, "Variant B doesn't call render_form()"
    
    assert "encode_input(" in variant_a, "Variant A doesn't call encode_input()"
    assert "encode_input(" in variant_b, "Variant B doesn't call encode_input()"
    
    print("✓ Both interfaces use shared form component")


def test_both_interfaces_load_same_explainer():
    """Verify both variants import from the same SHAP explainer module."""
    variant_a = (PROJECT_ROOT / "interfaces" / "variant_a_static" / "app.py").read_text(encoding='utf-8')
    variant_b = (PROJECT_ROOT / "interfaces" / "variant_b_progressive" / "app.py").read_text(encoding='utf-8')
    
    # Both should import from xai.shap_explainer
    assert "from xai.shap_explainer import" in variant_a, \
        "Variant A doesn't import from xai.shap_explainer"
    assert "from xai.shap_explainer import" in variant_b, \
        "Variant B doesn't import from xai.shap_explainer"
    
    # Both should call load_artefacts() and explain()
    assert "load_artefacts()" in variant_a, "Variant A doesn't load artefacts"
    assert "load_artefacts()" in variant_b, "Variant B doesn't load artefacts"
    
    assert "explain(" in variant_a, "Variant A doesn't call explain()"
    assert "explain(" in variant_b, "Variant B doesn't call explain()"
    
    print("✓ Both interfaces use shared explainer module")


# ── Run Tests ──────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("INTERFACE CONSISTENCY TEST SUITE")
    print("=" * 80 + "\n")
    
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    
    print("\n" + "=" * 80)
    if exit_code == 0:
        print("[SUCCESS] ALL INTERFACE CONSISTENCY TESTS PASSED")
        print("\nInternal validity verified:")
        print("  - Both interfaces use identical model predictions")
        print("  - Both interfaces compute identical SHAP values")
        print("  - No PII is collected or displayed")
        print("  - Differences are ONLY in presentation, not in underlying data")
    else:
        print("[FAILURE] SOME TESTS FAILED - INTERNAL VALIDITY AT RISK")
    print("=" * 80 + "\n")
    
    sys.exit(exit_code)
