"""
Sample test file for Eligibility Checker
Demonstrates how to write tests for the application
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Scheme, UserProfile
from src.eligibility_checker import EligibilityChecker


def test_age_matching():
    """Test age-based matching."""
    # Create a test scheme with age restriction
    scheme = Scheme(
        scheme_name="Test Youth Scheme",
        state_name="Bihar",
        scheme_url="http://test.com",
        details="Scheme for youth",
        benefits=["Benefit 1"],
        eligibility=["Age between 18 and 35 years"],
        application_process=["Step 1"],
        documents_required=["Aadhaar"],
        faqs=[]
    )
    
    # Test user within age range
    user_in_range = UserProfile(age=25, gender="Male", category="General")
    score, reasons = scheme.calculate_match_score(user_in_range)
    assert score > 0, "User within age range should have positive score"
    
    # Test user outside age range
    user_out_range = UserProfile(age=50, gender="Male", category="General")
    score, reasons = scheme.calculate_match_score(user_out_range)
    assert score == 0, "User outside age range should have zero score"
    
    print("✓ Age matching test passed")


def test_gender_matching():
    """Test gender-based matching."""
    scheme = Scheme(
        scheme_name="Women Empowerment Scheme",
        state_name="Bihar",
        scheme_url="http://test.com",
        details="Scheme for women",
        benefits=["Benefit 1"],
        eligibility=["Female applicants only", "Age 18 to 60"],
        application_process=["Step 1"],
        documents_required=["Aadhaar"],
        faqs=[]
    )
    
    # Female user should match
    female_user = UserProfile(age=30, gender="Female", category="General")
    score, reasons = scheme.calculate_match_score(female_user)
    assert score > 0, "Female user should match female-only scheme"
    
    # Male user should not match
    male_user = UserProfile(age=30, gender="Male", category="General")
    score, reasons = scheme.calculate_match_score(male_user)
    assert score == 0, "Male user should not match female-only scheme"
    
    print("✓ Gender matching test passed")


def test_category_matching():
    """Test category-based matching."""
    scheme = Scheme(
        scheme_name="SC/ST Welfare Scheme",
        state_name="Bihar",
        scheme_url="http://test.com",
        details="Scheme for SC and ST categories",
        benefits=["Benefit 1"],
        eligibility=["Scheduled Caste or Scheduled Tribe category", "Age 18-60"],
        application_process=["Step 1"],
        documents_required=["Caste Certificate"],
        faqs=[]
    )
    
    # SC user should match
    sc_user = UserProfile(age=30, gender="Male", category="SC")
    score, reasons = scheme.calculate_match_score(sc_user)
    assert score > 0, "SC user should match SC/ST scheme"
    
    # General category might have lower score
    general_user = UserProfile(age=30, gender="Male", category="General")
    score_general, _ = scheme.calculate_match_score(general_user)
    score_sc, _ = scheme.calculate_match_score(sc_user)
    assert score_sc >= score_general, "SC user should score same or higher than General"
    
    print("✓ Category matching test passed")


def test_income_matching():
    """Test income-based matching."""
    scheme = Scheme(
        scheme_name="Low Income Support",
        state_name="Bihar",
        scheme_url="http://test.com",
        details="For families with income below ₹60,000",
        benefits=["Financial support"],
        eligibility=["Annual income less than ₹60,000", "Age 18-60"],
        application_process=["Step 1"],
        documents_required=["Income Certificate"],
        faqs=[]
    )
    
    # User with eligible income
    low_income_user = UserProfile(age=30, gender="Male", category="General", annual_income=50000)
    score, reasons = scheme.calculate_match_score(low_income_user)
    assert score > 0, "User with eligible income should match"
    
    # User with too high income
    high_income_user = UserProfile(age=30, gender="Male", category="General", annual_income=100000)
    score, reasons = scheme.calculate_match_score(high_income_user)
    assert score == 0, "User with income above limit should not match"
    
    print("✓ Income matching test passed")


def test_eligibility_checker():
    """Test the EligibilityChecker class."""
    # Create test schemes
    schemes = [
        Scheme(
            scheme_name="Youth Scheme",
            state_name="Bihar",
            scheme_url="http://test.com",
            details="For youth",
            benefits=["Support"],
            eligibility=["Age 18-35"],
            application_process=["Apply"],
            documents_required=["ID"],
            faqs=[]
        ),
        Scheme(
            scheme_name="Senior Scheme",
            state_name="Bihar",
            scheme_url="http://test.com",
            details="For seniors",
            benefits=["Pension"],
            eligibility=["Age 60 and above"],
            application_process=["Apply"],
            documents_required=["Age Proof"],
            faqs=[]
        )
    ]
    
    checker = EligibilityChecker(schemes)
    
    # Young user should match Youth Scheme
    young_user = UserProfile(age=25, gender="Male", category="General")
    eligible = checker.find_eligible_schemes(young_user, min_score=10)
    
    assert len(eligible) > 0, "Young user should find eligible schemes"
    assert eligible[0][0].scheme_name == "Youth Scheme", "Top match should be Youth Scheme"
    
    # Senior user should match Senior Scheme
    senior_user = UserProfile(age=65, gender="Male", category="General")
    eligible = checker.find_eligible_schemes(senior_user, min_score=10)
    
    assert len(eligible) > 0, "Senior user should find eligible schemes"
    
    print("✓ EligibilityChecker test passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Running Tests for Scheme Finder")
    print("="*60 + "\n")
    
    try:
        test_age_matching()
        test_gender_matching()
        test_category_matching()
        test_income_matching()
        test_eligibility_checker()
        
        print("\n" + "="*60)
        print("✓ All tests passed successfully!")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    run_all_tests()
