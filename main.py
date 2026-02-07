"""
Scheme Finder - Main Application
Government Scheme Recommendation System for Bihar

This application helps citizens find eligible government schemes based on their profile.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scheme_loader import SchemeLoader
from src.eligibility_checker import EligibilityChecker
from src.questionnaire import Questionnaire
from src.report_generator import ReportGenerator
from src.models import UserProfile


class SchemeFinder:
    """
    Main application class for Scheme Finder.
    """
    
    def __init__(self, data_file: str = "data/schemes_data.csv"):
        """
        Initialize the Scheme Finder application.
        
        Args:
            data_file: Path to the CSV file containing scheme data
        """
        self.data_file = data_file
        self.schemes = []
        self.checker = None
        
    def initialize(self):
        """Load schemes and initialize the checker."""
        print("\n🚀 Initializing Scheme Finder...")
        
        # Load schemes
        loader = SchemeLoader(self.data_file)
        self.schemes = loader.load_schemes()
        
        # Initialize eligibility checker
        self.checker = EligibilityChecker(self.schemes)
        
        # Show statistics
        stats = self.checker.get_statistics()
        print(f"📊 Database Statistics:")
        print(f"   • Total Schemes: {stats['total_schemes']}")
        print(f"   • States Covered: {', '.join(stats['by_state'].keys())}")
        print(f"   • Schemes for SC/ST: {stats['by_category']['SC'] + stats['by_category']['ST']}")
        print(f"   • Schemes for Women: {stats['by_gender']['Female']}")
        print(f"   • Schemes for BPL: {stats['for_bpl']}")
        print(f"   • Schemes for Disabled: {stats['for_disabled']}")
        print()
    
    def run_interactive(self):
        """Run in interactive mode with full questionnaire."""
        print("\n" + "="*80)
        print("           WELCOME TO GOVERNMENT SCHEME FINDER")
        print("           Find Government Schemes You're Eligible For!")
        print("="*80)
        
        # Collect user information
        questionnaire = Questionnaire()
        user_profile = questionnaire.run()
        
        # Find eligible schemes
        eligible_schemes = self.checker.find_eligible_schemes(user_profile, min_score=40)
        
        # Generate and display report
        report = ReportGenerator.generate_console_report(
            user_profile, 
            eligible_schemes,
            show_details=True
        )
        print(report)
        
        # Ask if user wants to save report
        save_report = input("\n💾 Would you like to save this report to a file? (y/n): ").strip().lower()
        if save_report in ['y', 'yes']:
            ReportGenerator.save_to_file(report)
        
        # Offer to show detailed scheme info
        if eligible_schemes:
            self._show_scheme_details(eligible_schemes)
    
    def run_quick_mode(self):
        """Run in quick mode with minimal questions."""
        print("\n" + "="*80)
        print("           GOVERNMENT SCHEME FINDER - QUICK MODE")
        print("="*80)
        
        # Collect minimal information
        questionnaire = Questionnaire()
        user_profile = questionnaire.quick_mode()
        
        # Find top schemes
        top_schemes = self.checker.get_top_schemes(user_profile, limit=5)
        
        # Generate and display report
        report = ReportGenerator.generate_console_report(
            user_profile, 
            top_schemes,
            show_details=False
        )
        print(report)
    
    def _show_scheme_details(self, eligible_schemes):
        """Show detailed information about a specific scheme."""
        while True:
            choice = input("\n🔍 Enter scheme number to see full details (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                break
            
            try:
                scheme_num = int(choice)
                if 1 <= scheme_num <= len(eligible_schemes):
                    scheme = eligible_schemes[scheme_num - 1][0]
                    detailed_report = ReportGenerator.generate_detailed_scheme_report(scheme)
                    print(detailed_report)
                else:
                    print(f"⚠ Please enter a number between 1 and {len(eligible_schemes)}")
            except ValueError:
                print("⚠ Please enter a valid number or 'q' to quit")
    
    def search_by_name(self, scheme_name: str):
        """Search for a specific scheme by name."""
        loader = SchemeLoader(self.data_file)
        scheme = loader.get_scheme_by_name(scheme_name)
        
        if scheme:
            report = ReportGenerator.generate_detailed_scheme_report(scheme)
            print(report)
        else:
            print(f"\n❌ Scheme '{scheme_name}' not found in database.")


def show_menu():
    """Display the main menu."""
    print("\n" + "="*80)
    print("                    MAIN MENU")
    print("="*80)
    print("1. Find Schemes (Complete Questionnaire)")
    print("2. Quick Find (Essential Questions Only)")
    print("3. View All Schemes")
    print("4. Search Scheme by Name")
    print("5. Exit")
    print("="*80)


def main():
    """Main entry point of the application."""
    app = SchemeFinder()
    
    try:
        app.initialize()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("Please ensure 'schemes_data.csv' exists in the 'data' folder.")
        return
    except Exception as e:
        print(f"\n❌ Unexpected error during initialization: {e}")
        return
    
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            app.run_interactive()
        
        elif choice == '2':
            app.run_quick_mode()
        
        elif choice == '3':
            print(f"\n📚 Total Schemes Available: {len(app.schemes)}")
            for i, scheme in enumerate(app.schemes, 1):
                print(f"{i}. {scheme.scheme_name} ({scheme.state_name})")
            
            # Option to view details
            view_choice = input("\nEnter scheme number to view details (or press Enter to continue): ").strip()
            if view_choice.isdigit():
                idx = int(view_choice) - 1
                if 0 <= idx < len(app.schemes):
                    report = ReportGenerator.generate_detailed_scheme_report(app.schemes[idx])
                    print(report)
        
        elif choice == '4':
            search_name = input("\n🔍 Enter scheme name to search: ").strip()
            app.search_by_name(search_name)
        
        elif choice == '5':
            print("\n" + "="*80)
            print("     Thank you for using Government Scheme Finder!")
            print("     Stay informed, Stay empowered!")
            print("="*80 + "\n")
            break
        
        else:
            print("\n⚠ Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
