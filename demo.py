"""
Demo Script - Demonstrates Scheme Finder capabilities
Run this to see a quick demonstration of the system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scheme_loader import SchemeLoader
from src.eligibility_checker import EligibilityChecker
from src.models import UserProfile
from src.report_generator import ReportGenerator


def demo_student_profile():
    """Demo for a student profile."""
    print("\n" + "="*80)
    print("DEMO 1: Student from SC Category")
    print("="*80)
    
    student = UserProfile(
        state="Bihar",
        age=22,
        gender="Male",
        category="SC",
        occupation="Student",
        education_level="Graduate",
        annual_income=45000,
        is_bpl=False,
        has_disability=False,
        marital_status="Single",
        district="Patna"
    )
    
    return student


def demo_farmer_profile():
    """Demo for a farmer profile."""
    print("\n" + "="*80)
    print("DEMO 2: Farmer with Agricultural Land")
    print("="*80)
    
    farmer = UserProfile(
        state="Bihar",
        age=35,
        gender="Male",
        category="BC",
        occupation="Farmer",
        owns_agricultural_land=True,
        land_size_acres=2.5,
        education_level="10th/Matriculation",
        annual_income=55000,
        is_bpl=True,
        has_disability=False,
        marital_status="Married",
        district="Saran"
    )
    
    return farmer


def demo_entrepreneur_profile():
    """Demo for an entrepreneur profile."""
    print("\n" + "="*80)
    print("DEMO 3: Young Entrepreneur (Startup)")
    print("="*80)
    
    entrepreneur = UserProfile(
        state="Bihar",
        age=28,
        gender="Female",
        category="EBC",
        occupation="Entrepreneur/Business Owner",
        business_type="Startup",
        education_level="Graduate",
        annual_income=150000,
        is_bpl=False,
        has_disability=False,
        marital_status="Single",
        district="Patna"
    )
    
    return entrepreneur


def demo_widow_profile():
    """Demo for a widow seeking support."""
    print("\n" + "="*80)
    print("DEMO 4: Widow Seeking Social Security")
    print("="*80)
    
    widow = UserProfile(
        state="Bihar",
        age=45,
        gender="Female",
        category="General",
        occupation="Unemployed",
        education_level="Below 10th",
        annual_income=25000,
        is_bpl=True,
        has_disability=False,
        marital_status="Widow/Widower",
        district="Gopalganj"
    )
    
    return widow


def demo_disabled_person_profile():
    """Demo for person with disability."""
    print("\n" + "="*80)
    print("DEMO 5: Person with Disability")
    print("="*80)
    
    disabled = UserProfile(
        state="Bihar",
        age=32,
        gender="Male",
        category="SC",
        occupation="Unorganized Sector Worker",
        education_level="12th/Intermediate",
        annual_income=35000,
        is_bpl=False,
        has_disability=True,
        marital_status="Married",
        district="Patna"
    )
    
    return disabled


def run_demo():
    """Run complete demonstration."""
    print("\n" + "🌟"*40)
    print("\n          SCHEME FINDER - DEMONSTRATION")
    print("          Showing different user scenarios\n")
    print("🌟"*40)
    
    # Initialize system
    print("\n⚙️  Initializing Scheme Finder...")
    loader = SchemeLoader("data/schemes_data.csv")
    schemes = loader.load_schemes()
    checker = EligibilityChecker(schemes)
    
    # Demo profiles
    profiles = [
        ("Student (SC, Age 22)", demo_student_profile()),
        ("Farmer (BC, 2.5 acres land)", demo_farmer_profile()),
        ("Female Entrepreneur (EBC, Startup)", demo_entrepreneur_profile()),
        ("Widow (BPL, Age 45)", demo_widow_profile()),
        ("Disabled Worker (SC, Age 32)", demo_disabled_person_profile())
    ]
    
    # Run each demo
    for title, profile in profiles:
        print(f"\n{'─'*80}")
        print(f"Profile: {title}")
        print(f"{'─'*80}")
        
        # Find schemes
        eligible = checker.get_top_schemes(profile, limit=5)
        
        if eligible:
            print(f"\n✓ Found {len(eligible)} eligible schemes:")
            for i, (scheme, score, reasons) in enumerate(eligible, 1):
                print(f"\n{i}. {scheme.scheme_name}")
                print(f"   Match Score: {score:.1f}/100")
                if reasons:
                    print(f"   Top Reason: {reasons[0]}")
        else:
            print("\n❌ No schemes found for this profile")
        
        input("\n[Press Enter to continue to next demo...]")
    
    # Statistics
    print("\n" + "="*80)
    print("SYSTEM STATISTICS")
    print("="*80)
    
    stats = checker.get_statistics()
    print(f"\n📊 Database Overview:")
    print(f"   Total Schemes: {stats['total_schemes']}")
    print(f"   For SC Category: {stats['by_category']['SC']}")
    print(f"   For ST Category: {stats['by_category']['ST']}")
    print(f"   For BC Category: {stats['by_category']['BC']}")
    print(f"   For EBC Category: {stats['by_category']['EBC']}")
    print(f"   For Women: {stats['by_gender']['Female']}")
    print(f"   For BPL: {stats['for_bpl']}")
    print(f"   For Disabled: {stats['for_disabled']}")
    print(f"   With Age Limits: {stats['with_age_limit']}")
    print(f"   With Income Limits: {stats['with_income_limit']}")
    
    print("\n" + "="*80)
    print("✓ Demonstration Complete!")
    print("="*80)
    print("\nRun 'python main.py' to use the full interactive application.\n")


if __name__ == "__main__":
    try:
        run_demo()
    except FileNotFoundError:
        print("\n❌ Error: schemes_data.csv not found in data/ folder")
        print("Please ensure the data file exists before running the demo.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
