"""
Test Script for Study System
─────────────────────────────────────────────────────────────────────────────
Verifies that all components are working correctly before running actual study.

Run: python test_study_system.py
─────────────────────────────────────────────────────────────────────────────
"""

import json
from pathlib import Path
from study_response_logger import StudyResponseLogger
from interfaces.shared_components.participant_session import get_next_participant_id

def test_task_cases():
    """Test that task cases load correctly."""
    print("\n" + "="*80)
    print("TEST 1: Task Cases")
    print("="*80)
    
    cases_file = Path("study_task_cases.json")
    if not cases_file.exists():
        print("❌ FAIL: study_task_cases.json not found")
        return False
    
    with open(cases_file, 'r') as f:
        data = json.load(f)
    
    cases = data.get('cases', [])
    print(f"✅ Loaded {len(cases)} task cases")
    
    # Check required cases for both variants
    variant_a_tasks = ["high_risk_1", "medium_risk_4", "low_risk_7"]
    variant_b_tasks = ["high_risk_2", "medium_risk_5", "low_risk_8"]
    
    case_ids = [c['case_id'] for c in cases]
    
    for task_id in variant_a_tasks + variant_b_tasks:
        if task_id in case_ids:
            print(f"  ✅ {task_id} found")
        else:
            print(f"  ❌ {task_id} MISSING")
            return False
    
    return True


def test_logger():
    """Test that logger creates files correctly."""
    print("\n" + "="*80)
    print("TEST 2: Response Logger")
    print("="*80)
    
    logger = StudyResponseLogger(output_dir="study_data_test")
    print("✅ Logger initialized")
    
    # Check files created
    files = [
        "demographics.csv",
        "sus_responses.csv",
        "trust_responses.csv",
        "understanding_responses.csv",
        "decision_confidence.csv",
        "qualitative_feedback.csv"
    ]
    
    for fname in files:
        fpath = Path("study_data_test") / fname
        if fpath.exists():
            print(f"  ✅ {fname} created")
        else:
            print(f"  ❌ {fname} NOT CREATED")
            return False
    
    # Test logging demographics
    logger.log_demographics("TEST001", {
        'age_group': '30-39',
        'gender': 'Female',
        'education_level': 'Masters',
        'role': 'Test User',
        'years_experience': '3-5 years',
        'ai_experience': 2,
        'familiarity_with_analytics': 3
    })
    print("✅ Demographics logged")
    
    # Test logging SUS
    logger.log_sus("TEST001", "variant_a", [4, 2, 5, 2, 4, 1, 4, 2, 5, 1])
    print("✅ SUS logged")
    
    # Test logging Trust
    logger.log_trust("TEST001", "variant_a", [4, 5, 4, 5, 4])
    print("✅ Trust logged")
    
    # Test logging Understanding
    logger.log_understanding("TEST001", "variant_a", [5, 4, 5, 4, 5])
    print("✅ Understanding logged")
    
    # Test logging Decision Confidence
    logger.log_decision_confidence("TEST001", "variant_a", "high_risk_1", [4, 4, 3, 4])
    print("✅ Decision confidence logged")
    
    # Test logging Qualitative
    logger.log_qualitative_feedback(
        "TEST001",
        q1_most_useful="Test response 1",
        q2_challenges="Test response 2",
        q3_improvements="Test response 3",
        q4_preference="Static",
        q4_preference_reason="Test reason"
    )
    print("✅ Qualitative feedback logged")
    
    return True


def test_participant_id_generation():
    """Test participant ID auto-generation."""
    print("\n" + "="*80)
    print("TEST 3: Participant ID Generation")
    print("="*80)
    
    # Create test logger to ensure demographics.csv exists
    logger = StudyResponseLogger(output_dir="study_data_test")
    
    # Test ID generation
    pid1 = get_next_participant_id("study_data_test")
    print(f"  Generated ID: {pid1}")
    
    if pid1 != "P001":
        print(f"  ❌ Expected P001, got {pid1}")
        return False
    
    print("  ✅ First ID is P001")
    
    # Log demographics to increment
    logger.log_demographics(pid1, {
        'age_group': '30-39',
        'gender': 'Female',
        'education_level': 'Masters',
        'role': 'Test',
        'years_experience': '3-5 years',
        'ai_experience': 2,
        'familiarity_with_analytics': 3
    })
    
    # Get next ID
    pid2 = get_next_participant_id("study_data_test")
    print(f"  Generated ID: {pid2}")
    
    if pid2 != "P002":
        print(f"  ❌ Expected P002, got {pid2}")
        return False
    
    print("  ✅ Second ID is P002")
    
    return True


def test_file_structure():
    """Test that all required files exist."""
    print("\n" + "="*80)
    print("TEST 4: File Structure")
    print("="*80)
    
    required_files = [
        "study_task_cases.json",
        "study_response_logger.py",
        "interfaces/shared_components/participant_session.py",
        "interfaces/shared_components/questionnaire_forms.py",
        "interfaces/variant_a_static/app_with_study.py",
        "interfaces/variant_b_progressive/app_with_study.py",
        "interfaces/final_feedback_app.py",
    ]
    
    all_exist = True
    for fpath in required_files:
        if Path(fpath).exists():
            print(f"  ✅ {fpath}")
        else:
            print(f"  ❌ {fpath} MISSING")
            all_exist = False
    
    return all_exist


def cleanup_test_data():
    """Remove test data directory."""
    import shutil
    test_dir = Path("study_data_test")
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("\n✅ Test data cleaned up")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("STUDY SYSTEM TEST SUITE")
    print("="*80)
    
    tests = [
        ("Task Cases", test_task_cases),
        ("Response Logger", test_logger),
        ("Participant ID Generation", test_participant_id_generation),
        ("File Structure", test_file_structure),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} FAILED with exception: {e}")
            results.append((name, False))
    
    # Cleanup
    cleanup_test_data()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "="*80)
    print(f"OVERALL: {passed}/{total} tests passed")
    print("="*80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready for study.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED. Fix issues before running study.")
        return 1


if __name__ == "__main__":
    exit(main())
