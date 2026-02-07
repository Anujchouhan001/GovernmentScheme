"""
Questionnaire - Interactive CLI to collect user information.
"""

from src.models import UserProfile


class Questionnaire:
    """
    Interactive questionnaire to collect user information for scheme matching.
    """
    
    def __init__(self):
        """Initialize the questionnaire."""
        self.user_profile = UserProfile()
    
    def run(self) -> UserProfile:
        """
        Run the complete questionnaire and return user profile.
        
        Returns:
            Completed UserProfile object
        """
        print("\n" + "="*70)
        print("     GOVERNMENT SCHEME FINDER - USER QUESTIONNAIRE")
        print("="*70)
        print("\nPlease answer the following questions to find suitable schemes.\n")
        
        # Section 1: Basic Demographics
        self._section_basic_demographics()
        
        # Section 2: Professional/Occupational
        self._section_professional()
        
        # Section 3: Educational Background
        self._section_education()
        
        # Section 4: Financial & Social Conditions
        self._section_financial_social()
        
        # Section 5: Location
        self._section_location()
        
        print("\n" + "="*70)
        print("✓ Questionnaire completed! Searching for eligible schemes...")
        print("="*70 + "\n")
        
        return self.user_profile
    
    def _section_basic_demographics(self):
        """Collect basic demographic information."""
        print("─" * 70)
        print("SECTION 1: BASIC DEMOGRAPHICS")
        print("─" * 70)
        
        # State
        self.user_profile.state = self._ask_choice(
            "What is your state of permanent residence?",
            ["Bihar", "Other"],
            default="Bihar"
        )
        
        # Age
        self.user_profile.age = self._ask_number(
            "What is your current age?",
            min_val=1,
            max_val=120
        )
        
        # Gender
        self.user_profile.gender = self._ask_choice(
            "What is your gender?",
            ["Male", "Female", "Transgender"]
        )
        
        # Category
        self.user_profile.category = self._ask_choice(
            "Which social category do you belong to?",
            ["General", "EWS", "BC", "EBC", "SC", "ST"]
        )
    
    def _section_professional(self):
        """Collect professional/occupational information."""
        print("\n" + "─" * 70)
        print("SECTION 2: PROFESSIONAL/OCCUPATIONAL STATUS")
        print("─" * 70)
        
        # Occupation
        self.user_profile.occupation = self._ask_choice(
            "What is your primary occupation?",
            [
                "Student",
                "Farmer",
                "Construction Worker",
                "Entrepreneur/Business Owner",
                "Fisherman",
                "Unorganized Sector Worker",
                "Artisan/Craftsman",
                "Unemployed",
                "Other"
            ]
        )
        
        # Follow-up questions based on occupation
        if self.user_profile.occupation == "Farmer":
            self.user_profile.owns_agricultural_land = self._ask_yes_no(
                "Do you own agricultural land?"
            )
            
            if self.user_profile.owns_agricultural_land:
                self.user_profile.land_size_acres = self._ask_number(
                    "What is the size of your land in acres?",
                    min_val=0.0,
                    allow_decimal=True
                )
        
        elif self.user_profile.occupation == "Construction Worker":
            self.user_profile.is_registered_worker = self._ask_yes_no(
                "Are you registered with Bihar Building & Other Construction Workers Welfare Board?"
            )
        
        elif self.user_profile.occupation == "Entrepreneur/Business Owner":
            self.user_profile.business_type = self._ask_choice(
                "What is your business type?",
                ["Startup", "Proprietorship", "Partnership", "Not Registered"]
            )
        
        elif self.user_profile.occupation == "Fisherman":
            self.user_profile.has_water_body_access = self._ask_yes_no(
                "Do you have access to water bodies (Wetlands, Ponds, Lakes)?"
            )
            
            if self.user_profile.has_water_body_access:
                self.user_profile.water_body_type = self._ask_text(
                    "What type of water body? (e.g., Man, Chaur, Lake)"
                )
    
    def _section_education(self):
        """Collect educational background."""
        print("\n" + "─" * 70)
        print("SECTION 3: EDUCATIONAL BACKGROUND")
        print("─" * 70)
        
        self.user_profile.education_level = self._ask_choice(
            "What is your highest educational qualification?",
            [
                "Below 10th",
                "10th/Matriculation",
                "12th/Intermediate",
                "ITI/Polytechnic Diploma",
                "Graduate",
                "Post-Graduate",
                "Other"
            ]
        )
        
        self.user_profile.cleared_competitive_exam = self._ask_yes_no(
            "Have you recently cleared any competitive exams (UPSC, BPSC, SSC, Banking)?"
        )
    
    def _section_financial_social(self):
        """Collect financial and social information."""
        print("\n" + "─" * 70)
        print("SECTION 4: FINANCIAL & SOCIAL CONDITIONS")
        print("─" * 70)
        
        self.user_profile.annual_income = self._ask_number(
            "What is your total annual family income (in ₹)?",
            min_val=0,
            allow_decimal=True
        )
        
        self.user_profile.is_bpl = self._ask_yes_no(
            "Do you belong to Below Poverty Line (BPL) category?"
        )
        
        self.user_profile.has_disability = self._ask_yes_no(
            "Do you have a physical disability (Divyangjan)?"
        )
        
        self.user_profile.marital_status = self._ask_choice(
            "What is your marital status?",
            ["Single", "Married", "Widow/Widower", "Divorced"]
        )
    
    def _section_location(self):
        """Collect location information."""
        print("\n" + "─" * 70)
        print("SECTION 5: LOCATION INFORMATION")
        print("─" * 70)
        
        bihar_districts = [
            "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Bhojpur",
            "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj", "Jamui",
            "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai",
            "Madhepura", "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Nawada",
            "Patna", "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura",
            "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali", "West Champaran", "Other"
        ]
        
        self.user_profile.district = self._ask_choice(
            "In which district do you reside?",
            bihar_districts
        )
    
    # Helper methods for asking questions
    
    def _ask_text(self, question: str) -> str:
        """Ask a text input question."""
        while True:
            response = input(f"\n{question}\n> ").strip()
            if response:
                return response
            print("⚠ Please provide an answer.")
    
    def _ask_number(
        self, 
        question: str, 
        min_val: float = None, 
        max_val: float = None,
        allow_decimal: bool = False
    ) -> float:
        """Ask a numeric input question."""
        while True:
            try:
                response = input(f"\n{question}\n> ").strip()
                
                if allow_decimal:
                    value = float(response)
                else:
                    value = int(response)
                
                if min_val is not None and value < min_val:
                    print(f"⚠ Value must be at least {min_val}")
                    continue
                
                if max_val is not None and value > max_val:
                    print(f"⚠ Value must not exceed {max_val}")
                    continue
                
                return value
                
            except ValueError:
                print("⚠ Please enter a valid number.")
    
    def _ask_choice(self, question: str, choices: list, default: str = None) -> str:
        """Ask a multiple choice question."""
        print(f"\n{question}")
        
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        while True:
            try:
                if default:
                    response = input(f"\nEnter choice (1-{len(choices)}) [Default: {default}]: ").strip()
                    if not response:
                        return default
                else:
                    response = input(f"\nEnter choice (1-{len(choices)}): ").strip()
                
                choice_num = int(response)
                
                if 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1]
                else:
                    print(f"⚠ Please enter a number between 1 and {len(choices)}")
                    
            except ValueError:
                print("⚠ Please enter a valid number.")
    
    def _ask_yes_no(self, question: str) -> bool:
        """Ask a yes/no question."""
        while True:
            response = input(f"\n{question} (y/n)\n> ").strip().lower()
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("⚠ Please answer 'y' for yes or 'n' for no.")
    
    def quick_mode(self) -> UserProfile:
        """
        Quick mode with minimal questions for testing.
        
        Returns:
            UserProfile with basic information
        """
        print("\n" + "="*70)
        print("     QUICK MODE - Essential Information Only")
        print("="*70 + "\n")
        
        self.user_profile.state = "Bihar"
        self.user_profile.age = self._ask_number("Your age:", min_val=1, max_val=120)
        self.user_profile.gender = self._ask_choice("Gender:", ["Male", "Female", "Transgender"])
        self.user_profile.category = self._ask_choice(
            "Category:", 
            ["General", "EWS", "BC", "EBC", "SC", "ST"]
        )
        self.user_profile.occupation = self._ask_choice(
            "Occupation:",
            ["Student", "Farmer", "Worker", "Entrepreneur", "Unemployed", "Other"]
        )
        self.user_profile.annual_income = self._ask_number(
            "Annual income (₹):", 
            min_val=0, 
            allow_decimal=True
        )
        
        return self.user_profile
