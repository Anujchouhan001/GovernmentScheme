"""
New Questionnaire System - Based on Excel scheme data
Asks all relevant questions and matches to exact eligible schemes
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class UserResponse:
    """Stores all user responses for scheme matching."""
    # Basic Info
    state_bihar: Optional[bool] = None
    age: Optional[int] = None
    gender: Optional[str] = None  # Male, Female, Transgender
    
    # Category
    category: Optional[str] = None  # General, BC, EBC, SC, ST, Minority
    is_bpl: Optional[bool] = None
    is_ultra_poor: Optional[bool] = None
    belong_to_rural_area: Optional[bool] = None
    
    # Family
    marital_status: Optional[str] = None  # Unmarried, Married, Divorced, Widowed, Abandoned, Remarried
    marriage_intercaste: Optional[bool] = None
    marriage_registered: Optional[bool] = None
    num_children: Optional[int] = None
    num_girl_children: Optional[int] = None
    girl_child_dob: Optional[str] = None
    
    # Financial
    annual_income: Optional[float] = None
    bank_account_linked_aadhaar: Optional[bool] = None
    has_aadhaar: Optional[bool] = None
    
    # Land & Property
    land_owned_acres: Optional[float] = None
    owns_house: Optional[bool] = None
    landless_houseless: Optional[bool] = None
    
    # Occupation
    occupation: Optional[str] = None  # Farmer, Student, Construction Worker, Business, etc.
    
    # Farmer specific
    is_farmer: Optional[bool] = None
    dbt_registered: Optional[bool] = None
    crop_damage_percent: Optional[float] = None
    
    # Construction Worker specific
    is_construction_worker: Optional[bool] = None
    bbocwwb_registered: Optional[bool] = None
    bbocwwb_membership_years: Optional[int] = None
    bbocwwb_active_membership: Optional[bool] = None
    completed_skill_training: Optional[bool] = None
    
    # Business/Startup specific
    is_business_owner: Optional[bool] = None
    business_type: Optional[str] = None  # Proprietorship, Partnership, Startup
    startup_registered_bihar: Optional[bool] = None
    startup_age_years: Optional[int] = None
    startup_turnover: Optional[float] = None
    startup_innovative: Optional[bool] = None
    startup_not_split: Optional[bool] = None
    
    # Student specific
    is_student: Optional[bool] = None
    education_level: Optional[str] = None
    education_institution_type: Optional[str] = None  # Government, Private, Anganwadi
    passed_10th_first_division: Optional[bool] = None
    passed_12th: Optional[bool] = None
    passed_from_bihar_board: Optional[bool] = None
    marks_10th_12th_above_60: Optional[bool] = None
    
    # Competitive Exam
    passed_upsc_prelim: Optional[bool] = None
    passed_bpsc_prelim: Optional[bool] = None
    passed_other_competitive_prelim: Optional[bool] = None
    
    # Hostel
    residing_in_hostel: Optional[bool] = None
    hostel_type: Optional[str] = None  # Government, Minority Welfare, SC/ST Welfare
    
    # Employment
    employment_status: Optional[str] = None  # Government, PSU, Semi-Govt, Private, Self-Employed, Unemployed
    is_retired_govt_employee: Optional[bool] = None
    
    # Disability
    has_disability: Optional[bool] = None
    disability_percentage: Optional[int] = None
    disability_type: Optional[str] = None  # Locomotor, Visual, Hearing, Other
    disability_nature: Optional[str] = None  # Permanent Total, Partial, Illness, Accident
    
    # Medical Conditions
    has_medical_condition: Optional[bool] = None
    medical_condition: Optional[str] = None  # Cancer, Heart Disease, AIDS, Leprosy
    
    # Journalist/Media
    is_journalist: Optional[bool] = None
    journalism_experience_years: Optional[int] = None
    
    # Fisherman
    is_fisherman: Optional[bool] = None
    fisher_cooperative_member: Optional[bool] = None
    has_pond_access: Optional[bool] = None
    pond_size_acres: Optional[float] = None
    
    # Unorganized Sector Worker
    is_unorganized_worker: Optional[bool] = None
    suffered_accidental_injury: Optional[bool] = None
    suffered_permanent_disability: Optional[bool] = None
    
    # Women specific
    is_pregnant_or_lactating: Optional[bool] = None
    willing_institutional_delivery: Optional[bool] = None
    
    # Death related (for family schemes)
    applying_for_death_benefit: Optional[bool] = None
    deceased_age: Optional[int] = None
    death_cause: Optional[str] = None  # Natural, Accident, Criminal, Suicide
    deceased_was_bbocwwb_registered: Optional[bool] = None
    is_legal_heir_or_dependent: Optional[bool] = None
    
    # Pension
    receiving_pension: Optional[bool] = None
    receiving_other_govt_pension: Optional[bool] = None
    
    # Other
    has_driving_license: Optional[bool] = None
    birth_registered: Optional[bool] = None
    district: Optional[str] = None
    
    # For milk producer scheme
    milk_producer_coop_member: Optional[bool] = None
    cattle_certified_healthy: Optional[bool] = None
    
    # PMAY-G
    pmay_g_beneficiary: Optional[bool] = None
    
    # Training
    completed_departmental_training: Optional[bool] = None
    
    # Previous benefit
    received_benefit_earlier: Optional[bool] = None


class SchemeQuestionnaire:
    """
    Dynamic questionnaire that asks questions based on the Excel scheme data
    and matches users to eligible schemes.
    """
    
    def __init__(self, json_path: str = "data/schemes_eligibility.json"):
        self.json_path = Path(json_path)
        self.schemes = self._load_schemes()
        self.user_response = UserResponse()
        self.questions_asked = set()
        
    def _load_schemes(self) -> List[Dict]:
        """Load schemes from JSON file."""
        if not self.json_path.exists():
            raise FileNotFoundError(f"Schemes file not found: {self.json_path}")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_questions(self) -> List[Dict[str, Any]]:
        """
        Get all unique questions that need to be asked.
        Returns structured question list with options.
        """
        questions = []
        question_map = {}
        
        # Define the master question list with proper order and options
        master_questions = [
            # Basic Demographics
            {
                "id": "state_bihar",
                "question": "Are you a resident of Bihar?",
                "type": "boolean",
                "section": "Basic Information",
                "required": True
            },
            {
                "id": "age",
                "question": "What is your age?",
                "type": "number",
                "min": 1,
                "max": 120,
                "section": "Basic Information",
                "required": True
            },
            {
                "id": "gender",
                "question": "What is your gender?",
                "type": "choice",
                "options": ["Male", "Female", "Transgender"],
                "section": "Basic Information",
                "required": True
            },
            
            # Category & Economic Status
            {
                "id": "category",
                "question": "Which social category do you belong to?",
                "type": "choice",
                "options": ["General", "BC (Backward Class)", "EBC (Extremely Backward Class)", 
                           "SC (Scheduled Caste)", "ST (Scheduled Tribe)", "Minority"],
                "section": "Category & Economic Status",
                "required": True
            },
            {
                "id": "is_bpl",
                "question": "Do you belong to a Below Poverty Line (BPL) family?",
                "type": "boolean",
                "section": "Category & Economic Status"
            },
            {
                "id": "annual_income",
                "question": "What is your annual family income (in ₹)?",
                "type": "number",
                "min": 0,
                "section": "Category & Economic Status",
                "required": True
            },
            {
                "id": "belong_to_rural_area",
                "question": "Do you live in a rural area?",
                "type": "boolean",
                "section": "Category & Economic Status"
            },
            
            # Identity Documents
            {
                "id": "has_aadhaar",
                "question": "Do you possess an Aadhaar number?",
                "type": "boolean",
                "section": "Identity Documents"
            },
            {
                "id": "bank_account_linked_aadhaar",
                "question": "Do you have a bank account linked with Aadhaar?",
                "type": "boolean",
                "section": "Identity Documents"
            },
            {
                "id": "dbt_registered",
                "question": "Are you registered on the Direct Benefit Transfer (DBT) portal?",
                "type": "boolean",
                "section": "Identity Documents"
            },
            {
                "id": "has_driving_license",
                "question": "Do you have a driving license?",
                "type": "boolean",
                "section": "Identity Documents"
            },
            
            # Marital Status
            {
                "id": "marital_status",
                "question": "What is your current marital status?",
                "type": "choice",
                "options": ["Unmarried", "Married", "Divorced", "Widowed", 
                           "Abandoned/Separated", "Remarried"],
                "section": "Marital Status"
            },
            {
                "id": "marriage_intercaste",
                "question": "Is your marriage an inter-caste marriage?",
                "type": "boolean",
                "section": "Marital Status",
                "condition": "marital_status == 'Married'"
            },
            {
                "id": "marriage_registered",
                "question": "Is your marriage registered?",
                "type": "boolean",
                "section": "Marital Status",
                "condition": "marital_status == 'Married'"
            },
            
            # Children
            {
                "id": "num_children",
                "question": "How many children do you have?",
                "type": "number",
                "min": 0,
                "max": 20,
                "section": "Family Information"
            },
            {
                "id": "num_girl_children",
                "question": "How many girl children do you have?",
                "type": "number",
                "min": 0,
                "max": 10,
                "section": "Family Information",
                "condition": "num_children > 0"
            },
            {
                "id": "birth_registered",
                "question": "Is your child's birth registered?",
                "type": "boolean",
                "section": "Family Information",
                "condition": "num_children > 0"
            },
            
            # Land & Property
            {
                "id": "land_owned_acres",
                "question": "How many acres of land do you own? (Enter 0 if none)",
                "type": "number",
                "min": 0,
                "section": "Land & Property"
            },
            {
                "id": "owns_house",
                "question": "Do you own a house?",
                "type": "boolean",
                "section": "Land & Property"
            },
            {
                "id": "landless_houseless",
                "question": "Are you landless and houseless?",
                "type": "boolean",
                "section": "Land & Property"
            },
            {
                "id": "pmay_g_beneficiary",
                "question": "Are you listed as a beneficiary under PMAY-G (Pradhan Mantri Awaas Yojana - Gramin)?",
                "type": "boolean",
                "section": "Land & Property"
            },
            
            # Occupation
            {
                "id": "occupation",
                "question": "What is your primary occupation?",
                "type": "choice",
                "options": ["Student", "Farmer", "Construction Worker", "Business Owner/Entrepreneur",
                           "Fisherman", "Unorganized Sector Worker/Craftsman", "Journalist/Media",
                           "Government Employee", "Private Employee", "Self-Employed", "Unemployed", "Other"],
                "section": "Occupation",
                "required": True
            },
            
            # Farmer Specific
            {
                "id": "is_farmer",
                "question": "Are you a farmer?",
                "type": "boolean",
                "section": "Farmer Details",
                "condition": "occupation == 'Farmer'"
            },
            {
                "id": "crop_damage_percent",
                "question": "What percentage of crop damage have you suffered due to natural calamities? (Enter 0 if none)",
                "type": "number",
                "min": 0,
                "max": 100,
                "section": "Farmer Details",
                "condition": "is_farmer == True"
            },
            
            # Construction Worker Specific
            {
                "id": "is_construction_worker",
                "question": "Are you engaged in building or construction work?",
                "type": "boolean",
                "section": "Construction Worker Details",
                "condition": "occupation == 'Construction Worker'"
            },
            {
                "id": "bbocwwb_registered",
                "question": "Are you registered with Bihar Building & Other Construction Workers Welfare Board (BBOCWWB)?",
                "type": "boolean",
                "section": "Construction Worker Details",
                "condition": "is_construction_worker == True"
            },
            {
                "id": "bbocwwb_membership_years",
                "question": "How many years of continuous membership do you have with BBOCWWB?",
                "type": "number",
                "min": 0,
                "section": "Construction Worker Details",
                "condition": "bbocwwb_registered == True"
            },
            {
                "id": "bbocwwb_active_membership",
                "question": "Is your BBOCWWB membership currently active?",
                "type": "boolean",
                "section": "Construction Worker Details",
                "condition": "bbocwwb_registered == True"
            },
            {
                "id": "completed_skill_training",
                "question": "Have you completed skill upgradation training?",
                "type": "boolean",
                "section": "Construction Worker Details",
                "condition": "is_construction_worker == True"
            },
            
            # Business/Startup Specific
            {
                "id": "is_business_owner",
                "question": "Are you a business owner or entrepreneur?",
                "type": "boolean",
                "section": "Business Details",
                "condition": "occupation == 'Business Owner/Entrepreneur'"
            },
            {
                "id": "business_type",
                "question": "What type of business do you have?",
                "type": "choice",
                "options": ["Proprietorship", "Partnership", "Startup", "Not Registered"],
                "section": "Business Details",
                "condition": "is_business_owner == True"
            },
            {
                "id": "startup_registered_bihar",
                "question": "Is your startup incorporated/registered in Bihar with an office in Bihar?",
                "type": "boolean",
                "section": "Business Details",
                "condition": "business_type == 'Startup'"
            },
            {
                "id": "startup_age_years",
                "question": "How many years ago was your entity incorporated?",
                "type": "number",
                "min": 0,
                "section": "Business Details",
                "condition": "business_type == 'Startup'"
            },
            {
                "id": "startup_turnover",
                "question": "What is the annual turnover of your entity (in ₹ crore)?",
                "type": "number",
                "min": 0,
                "section": "Business Details",
                "condition": "business_type == 'Startup'"
            },
            {
                "id": "startup_innovative",
                "question": "Does your startup work towards innovation or a scalable business model?",
                "type": "boolean",
                "section": "Business Details",
                "condition": "business_type == 'Startup'"
            },
            {
                "id": "startup_not_split",
                "question": "Was your entity NOT formed by splitting up or reconstructing an existing business?",
                "type": "boolean",
                "section": "Business Details",
                "condition": "business_type == 'Startup'"
            },
            
            # Student Specific
            {
                "id": "is_student",
                "question": "Are you currently a student?",
                "type": "boolean",
                "section": "Education Details",
                "condition": "occupation == 'Student'"
            },
            {
                "id": "education_level",
                "question": "What is your current education level?",
                "type": "choice",
                "options": ["Anganwadi (Pre-school)", "Class 1-5", "Class 6-8", "Class 9-10", 
                           "Class 11-12", "ITI", "Polytechnic Diploma", "Graduation", 
                           "Post-Graduation", "Not Currently Attending School"],
                "section": "Education Details"
            },
            {
                "id": "education_institution_type",
                "question": "What type of institution are you studying in?",
                "type": "choice",
                "options": ["Government School/College", "Government-Recognized Private Institution",
                           "Anganwadi Centre", "Madrasa", "Other"],
                "section": "Education Details",
                "condition": "is_student == True"
            },
            {
                "id": "passed_10th_first_division",
                "question": "Did you pass 10th class (Matric) with first division?",
                "type": "boolean",
                "section": "Education Details"
            },
            {
                "id": "passed_12th",
                "question": "Have you passed 12th class?",
                "type": "boolean",
                "section": "Education Details"
            },
            {
                "id": "passed_from_bihar_board",
                "question": "Did you pass from Bihar School Examination Board or Bihar Madrasa Education Board?",
                "type": "boolean",
                "section": "Education Details"
            },
            {
                "id": "marks_10th_12th_above_60",
                "question": "Did you score 60% or above marks in 10th or 12th examination?",
                "type": "boolean",
                "section": "Education Details"
            },
            
            # Competitive Exams
            {
                "id": "passed_upsc_prelim",
                "question": "Have you passed the UPSC preliminary examination?",
                "type": "boolean",
                "section": "Competitive Exams"
            },
            {
                "id": "passed_bpsc_prelim",
                "question": "Have you passed the BPSC preliminary examination?",
                "type": "boolean",
                "section": "Competitive Exams"
            },
            {
                "id": "passed_other_competitive_prelim",
                "question": "Have you passed any other competitive exam preliminary?",
                "type": "boolean",
                "section": "Competitive Exams"
            },
            
            # Hostel
            {
                "id": "residing_in_hostel",
                "question": "Are you currently residing in a hostel?",
                "type": "boolean",
                "section": "Hostel Details"
            },
            {
                "id": "hostel_type",
                "question": "What type of hostel are you residing in?",
                "type": "choice",
                "options": ["Government Hostel", "Minority Welfare Hostel", "SC/ST Welfare Hostel",
                           "OBC/EBC Welfare Hostel", "Private Hostel", "Other"],
                "section": "Hostel Details",
                "condition": "residing_in_hostel == True"
            },
            
            # Employment
            {
                "id": "employment_status",
                "question": "What is your employment status?",
                "type": "choice",
                "options": ["Government Employee", "PSU Employee", "Semi-Government Employee",
                           "Private Sector Employee", "Self-Employed", "Retired", "Unemployed"],
                "section": "Employment"
            },
            {
                "id": "is_retired_govt_employee",
                "question": "Are you a retired government employee?",
                "type": "boolean",
                "section": "Employment"
            },
            
            # Disability
            {
                "id": "has_disability",
                "question": "Do you have any disability?",
                "type": "boolean",
                "section": "Disability"
            },
            {
                "id": "disability_percentage",
                "question": "What is your disability percentage?",
                "type": "number",
                "min": 0,
                "max": 100,
                "section": "Disability",
                "condition": "has_disability == True"
            },
            {
                "id": "disability_type",
                "question": "What type of disability do you have?",
                "type": "choice",
                "options": ["Locomotor (difficulty in walking/movement)", "Visual (blindness/one eye affected)",
                           "Hearing/Speech", "Other Disability"],
                "section": "Disability",
                "condition": "has_disability == True"
            },
            {
                "id": "disability_nature",
                "question": "What is the nature of your disability?",
                "type": "choice",
                "options": ["Permanent Total", "Partial Disability (illness)", 
                           "Partial Disability (accident)", "Since Birth"],
                "section": "Disability",
                "condition": "has_disability == True"
            },
            
            # Medical Conditions
            {
                "id": "has_medical_condition",
                "question": "Do you have any of the following medical conditions: Cancer, Heart Disease, HIV/AIDS, Leprosy, or other serious/incurable disease?",
                "type": "boolean",
                "section": "Medical Conditions"
            },
            {
                "id": "medical_condition",
                "question": "Which medical condition do you have?",
                "type": "choice",
                "options": ["Cancer", "Heart Disease", "HIV/AIDS", "Leprosy", 
                           "Other Serious/Incurable Disease", "None"],
                "section": "Medical Conditions",
                "condition": "has_medical_condition == True"
            },
            
            # Journalist/Media
            {
                "id": "is_journalist",
                "question": "Are you a journalist or media representative?",
                "type": "boolean",
                "section": "Journalist Details",
                "condition": "occupation == 'Journalist/Media'"
            },
            {
                "id": "journalism_experience_years",
                "question": "How many years of work experience do you have as a journalist?",
                "type": "number",
                "min": 0,
                "section": "Journalist Details",
                "condition": "is_journalist == True"
            },
            
            # Fisherman Specific
            {
                "id": "is_fisherman",
                "question": "Are you a fisherman?",
                "type": "boolean",
                "section": "Fisherman Details",
                "condition": "occupation == 'Fisherman'"
            },
            {
                "id": "fisher_cooperative_member",
                "question": "Are you an active member of a Block Level Fishermen Cooperative?",
                "type": "boolean",
                "section": "Fisherman Details",
                "condition": "is_fisherman == True"
            },
            {
                "id": "has_pond_access",
                "question": "Do you own or lease land for fish pond construction?",
                "type": "boolean",
                "section": "Fisherman Details"
            },
            {
                "id": "pond_size_acres",
                "question": "What is the size of your pond (in acres)?",
                "type": "number",
                "min": 0,
                "section": "Fisherman Details",
                "condition": "has_pond_access == True"
            },
            
            # Unorganized Sector Worker
            {
                "id": "is_unorganized_worker",
                "question": "Are you a worker or craftsman in the unorganized sector?",
                "type": "boolean",
                "section": "Unorganized Sector",
                "condition": "occupation == 'Unorganized Sector Worker/Craftsman'"
            },
            {
                "id": "suffered_accidental_injury",
                "question": "Have you suffered an accidental injury?",
                "type": "boolean",
                "section": "Unorganized Sector"
            },
            {
                "id": "suffered_permanent_disability",
                "question": "Have you suffered total permanent disability due to an accident?",
                "type": "boolean",
                "section": "Unorganized Sector"
            },
            
            # Women Specific
            {
                "id": "is_pregnant_or_lactating",
                "question": "Are you currently pregnant or a lactating/nursing (breastfeeding) mother?",
                "type": "boolean",
                "section": "Women Specific",
                "condition": "gender == 'Female'"
            },
            {
                "id": "willing_institutional_delivery",
                "question": "Are you willing to undergo institutional delivery?",
                "type": "boolean",
                "section": "Women Specific",
                "condition": "is_pregnant_or_lactating == True"
            },
            
            # Death Benefit Related
            {
                "id": "applying_for_death_benefit",
                "question": "Are you applying for a death-related benefit (for a deceased family member)?",
                "type": "boolean",
                "section": "Death Benefit"
            },
            {
                "id": "deceased_age",
                "question": "What was the age of the deceased at the time of death?",
                "type": "number",
                "min": 0,
                "max": 120,
                "section": "Death Benefit",
                "condition": "applying_for_death_benefit == True"
            },
            {
                "id": "death_cause",
                "question": "What was the cause of death?",
                "type": "choice",
                "options": ["Natural Death", "Accident", "Criminal Incident", "Suicide", 
                           "Intoxication/Poisoning"],
                "section": "Death Benefit",
                "condition": "applying_for_death_benefit == True"
            },
            {
                "id": "deceased_was_bbocwwb_registered",
                "question": "Was the deceased registered with BBOCWWB?",
                "type": "boolean",
                "section": "Death Benefit",
                "condition": "applying_for_death_benefit == True"
            },
            {
                "id": "is_legal_heir_or_dependent",
                "question": "Are you a legal heir or dependent family member of the deceased?",
                "type": "boolean",
                "section": "Death Benefit",
                "condition": "applying_for_death_benefit == True"
            },
            
            # Pension
            {
                "id": "receiving_pension",
                "question": "Are you currently receiving any pension?",
                "type": "boolean",
                "section": "Pension"
            },
            {
                "id": "receiving_other_govt_pension",
                "question": "Are you receiving any other government or social-security pension?",
                "type": "boolean",
                "section": "Pension"
            },
            
            # Training
            {
                "id": "completed_departmental_training",
                "question": "Have you completed training under any departmental scheme?",
                "type": "boolean",
                "section": "Training"
            },
            
            # Previous Benefits
            {
                "id": "received_benefit_earlier",
                "question": "Have you already received this type of benefit earlier?",
                "type": "boolean",
                "section": "Previous Benefits"
            },
            
            # Milk Producer
            {
                "id": "milk_producer_coop_member",
                "question": "Are you a member of a Milk Producer Cooperative Committee?",
                "type": "boolean",
                "section": "Other"
            },
            {
                "id": "cattle_certified_healthy",
                "question": "Are your cattle healthy and certified by a veterinary doctor?",
                "type": "boolean",
                "section": "Other",
                "condition": "milk_producer_coop_member == True"
            },
            
            # District
            {
                "id": "district",
                "question": "Which district do you currently live in?",
                "type": "text",
                "section": "Location"
            }
        ]
        
        return master_questions
    
    def get_sections(self) -> List[str]:
        """Get all unique sections for the questionnaire."""
        questions = self.get_all_questions()
        sections = []
        for q in questions:
            if q["section"] not in sections:
                sections.append(q["section"])
        return sections
    
    def get_questions_by_section(self, section: str) -> List[Dict]:
        """Get questions for a specific section."""
        questions = self.get_all_questions()
        return [q for q in questions if q["section"] == section]
    
    def set_response(self, question_id: str, value: Any):
        """Set a user response."""
        if hasattr(self.user_response, question_id):
            setattr(self.user_response, question_id, value)
            self.questions_asked.add(question_id)
    
    def get_response(self, question_id: str) -> Any:
        """Get a user response."""
        return getattr(self.user_response, question_id, None)
    
    def find_eligible_schemes(self, only_fully_eligible: bool = True) -> List[Dict[str, Any]]:
        """
        Find all schemes the user is eligible for based on their responses.
        Returns list of eligible schemes with match details.
        
        Args:
            only_fully_eligible: If True, only return 100% matching schemes (default True)
        """
        eligible_schemes = []
        
        for scheme in self.schemes:
            is_eligible, match_details = self._check_scheme_eligibility(scheme)
            
            # Only include schemes that are fully eligible (100% match)
            if is_eligible:
                eligible_schemes.append({
                    "name": scheme["name"],
                    "matched_criteria": match_details["matched"],
                    "total_criteria": len(scheme["eligibility_criteria"]),
                    "match_percentage": match_details["match_percentage"],
                    "is_fully_eligible": True,
                    "failed_criteria": [],
                    "eligibility_criteria": scheme.get("eligibility_criteria", [])
                })
        
        # Sort by number of matched criteria (more criteria = more specific match)
        eligible_schemes.sort(key=lambda x: x["matched_criteria"], reverse=True)
        
        return eligible_schemes
    
    def _check_scheme_eligibility(self, scheme: Dict) -> tuple:
        """
        Check if user is eligible for a specific scheme.
        Returns (is_eligible, match_details)
        """
        criteria_list = scheme.get("eligibility_criteria", [])
        if not criteria_list:
            return False, {"matched": 0, "failed": [], "match_percentage": 0}
        
        matched_count = 0
        failed_criteria = []
        unanswered_count = 0
        
        for criteria in criteria_list:
            data_field = criteria.get("data_field", "")
            eligibility_text = criteria.get("eligibility_text", "").lower()
            
            # Check if we have a response for this criteria
            has_response = self._has_response_for_criteria(data_field, eligibility_text)
            
            if has_response:
                is_matched = self._evaluate_criteria(data_field, eligibility_text)
                if is_matched:
                    matched_count += 1
                else:
                    failed_criteria.append(criteria.get("question", eligibility_text))
            else:
                # If we don't have a response, count as unanswered (neutral)
                unanswered_count += 1
        
        total_criteria = len(criteria_list)
        answered_criteria = total_criteria - unanswered_count
        
        # Calculate match percentage based on answered criteria
        if answered_criteria > 0:
            match_percentage = (matched_count / answered_criteria * 100)
        else:
            match_percentage = 0
        
        # User is fully eligible if they matched all answered criteria and answered at least some
        is_eligible = (matched_count == answered_criteria) and (answered_criteria > 0) and (len(failed_criteria) == 0)
        
        return is_eligible, {
            "matched": matched_count,
            "failed": failed_criteria,
            "match_percentage": match_percentage,
            "answered": answered_criteria,
            "total": total_criteria
        }
    
    def _has_response_for_criteria(self, data_field: str, eligibility_text: str) -> bool:
        """Check if we have a response relevant to this criteria."""
        # Map data fields to user response attributes
        field_mapping = self._get_field_mapping()
        
        for key in field_mapping:
            if key in data_field.lower():
                user_field = field_mapping[key]
                if getattr(self.user_response, user_field, None) is not None:
                    return True
        
        return False
    
    def _evaluate_criteria(self, data_field: str, eligibility_text: str) -> bool:
        """Evaluate if user meets a specific eligibility criterion."""
        data_field_lower = data_field.lower()
        eligibility_lower = eligibility_text.lower()
        
        # State Bihar
        if "state_bihar" in data_field_lower or "resident of bihar" in eligibility_lower:
            return self.user_response.state_bihar == True
        
        # Age checks
        if data_field_lower == "age" or "age" in eligibility_lower:
            if self.user_response.age is not None:
                # Extract age range from eligibility text
                import re
                age_match = re.search(r'(\d+)\s*(?:and|to|-)\s*(\d+)', eligibility_lower)
                if age_match:
                    min_age, max_age = int(age_match.group(1)), int(age_match.group(2))
                    return min_age <= self.user_response.age <= max_age
                
                # Single age threshold
                age_single = re.search(r'(\d+)\s*(?:years?\s*(?:or|and)\s*(?:above|older|more)|\+)', eligibility_lower)
                if age_single:
                    min_age = int(age_single.group(1))
                    return self.user_response.age >= min_age
                
                return True  # No specific age criteria found
            return False
        
        # Gender
        if data_field_lower == "gender" or "female" in eligibility_lower or "male" in eligibility_lower:
            if "female" in eligibility_lower or "woman" in eligibility_lower or "girl" in eligibility_lower:
                return self.user_response.gender == "Female"
            if "male" in eligibility_lower and "female" not in eligibility_lower:
                return self.user_response.gender == "Male"
            return True
        
        # Category checks
        if "belong to" in data_field_lower or "category" in data_field_lower:
            user_cat = self.user_response.category
            if user_cat:
                user_cat_lower = user_cat.lower()
                if "sc" in eligibility_lower and "sc" in user_cat_lower:
                    return True
                if "st" in eligibility_lower and "st" in user_cat_lower:
                    return True
                if "bc" in eligibility_lower and "bc" in user_cat_lower:
                    return True
                if "ebc" in eligibility_lower and "ebc" in user_cat_lower:
                    return True
                if "obc" in eligibility_lower and ("bc" in user_cat_lower or "obc" in user_cat_lower):
                    return True
                if "minority" in eligibility_lower and "minority" in user_cat_lower:
                    return True
                if "general" in eligibility_lower and "general" in user_cat_lower:
                    return True
            return False
        
        # BPL check
        if "bpl" in data_field_lower or "below poverty line" in eligibility_lower:
            return self.user_response.is_bpl == True
        
        # Income checks
        if "income" in data_field_lower or "income" in eligibility_lower:
            if self.user_response.annual_income is not None:
                import re
                # Extract income limit
                income_match = re.search(r'₹\s*([\d,]+)', eligibility_lower)
                if income_match:
                    limit = float(income_match.group(1).replace(',', ''))
                    return self.user_response.annual_income <= limit
                
                # Check for income ranges like "60,000" or "4,00,000"
                income_match2 = re.search(r'([\d,]+)\s*(?:or less|or below|less than)', eligibility_lower)
                if income_match2:
                    limit = float(income_match2.group(1).replace(',', ''))
                    return self.user_response.annual_income <= limit
                
                return True
            return False
        
        # Land ownership
        if "land_owned" in data_field_lower or "acres" in eligibility_lower:
            if self.user_response.land_owned_acres is not None:
                import re
                land_match = re.search(r'([\d.]+)\s*(?:and|to|-)\s*([\d.]+)\s*acres', eligibility_lower)
                if land_match:
                    min_land, max_land = float(land_match.group(1)), float(land_match.group(2))
                    return min_land <= self.user_response.land_owned_acres <= max_land
                return self.user_response.land_owned_acres > 0
            return False
        
        # Farmer
        if "farmer" in data_field_lower or "farmer" in eligibility_lower:
            return self.user_response.occupation == "Farmer" or self.user_response.is_farmer == True
        
        # DBT registration
        if "dbt_registered" in data_field_lower or "dbt" in eligibility_lower:
            return self.user_response.dbt_registered == True
        
        # Construction worker
        if "construction_worker" in data_field_lower or "construction" in eligibility_lower:
            if "bbocwwb" in eligibility_lower or "registered" in eligibility_lower:
                return self.user_response.bbocwwb_registered == True
            return self.user_response.occupation == "Construction Worker" or self.user_response.is_construction_worker == True
        
        # BBOCWWB membership
        if "bbocwwb" in data_field_lower or "membership" in eligibility_lower:
            if "active" in eligibility_lower:
                return self.user_response.bbocwwb_active_membership == True
            if "year" in eligibility_lower:
                import re
                years_match = re.search(r'(\d+)\s*year', eligibility_lower)
                if years_match and self.user_response.bbocwwb_membership_years is not None:
                    required_years = int(years_match.group(1))
                    return self.user_response.bbocwwb_membership_years >= required_years
            return self.user_response.bbocwwb_registered == True
        
        # Student
        if "student" in data_field_lower or "student" in eligibility_lower:
            return self.user_response.occupation == "Student" or self.user_response.is_student == True
        
        # Education levels
        if "educational qualification" in data_field_lower or "class" in eligibility_lower:
            if "10th" in eligibility_lower or "matric" in eligibility_lower:
                if "first division" in eligibility_lower:
                    return self.user_response.passed_10th_first_division == True
                return self.user_response.education_level in ["Class 9-10", "Class 11-12", "ITI", 
                                                               "Polytechnic Diploma", "Graduation", "Post-Graduation"]
            if "12th" in eligibility_lower or "intermediate" in eligibility_lower:
                return self.user_response.passed_12th == True
            if "bihar board" in eligibility_lower:
                return self.user_response.passed_from_bihar_board == True
        
        # Competitive exams
        if "upsc" in eligibility_lower:
            return self.user_response.passed_upsc_prelim == True
        if "bpsc" in eligibility_lower:
            return self.user_response.passed_bpsc_prelim == True
        
        # Disability
        if "disabled" in data_field_lower or "disability" in eligibility_lower or "divyangjan" in eligibility_lower:
            return self.user_response.has_disability == True
        
        # Marital status
        if "marital" in data_field_lower:
            if "widow" in eligibility_lower:
                return self.user_response.marital_status == "Widowed"
            if "divorced" in eligibility_lower or "abandoned" in eligibility_lower:
                return self.user_response.marital_status in ["Divorced", "Abandoned/Separated"]
            if "remarried" in eligibility_lower and "not" in eligibility_lower:
                return self.user_response.marital_status != "Remarried"
            if "inter-caste" in eligibility_lower or "intercaste" in eligibility_lower:
                return self.user_response.marriage_intercaste == True
            if "registered" in eligibility_lower:
                return self.user_response.marriage_registered == True
        
        # Minority
        if "minority" in data_field_lower or "minority" in eligibility_lower:
            return self.user_response.category == "Minority"
        
        # Business/Startup
        if "business" in data_field_lower or "startup" in eligibility_lower:
            if "proprietorship" in eligibility_lower or "partnership" in eligibility_lower:
                return self.user_response.business_type in ["Proprietorship", "Partnership"]
            if "startup" in data_field_lower:
                if "registered in bihar" in eligibility_lower:
                    return self.user_response.startup_registered_bihar == True
                if "innovation" in eligibility_lower or "scalable" in eligibility_lower:
                    return self.user_response.startup_innovative == True
                if "turnover" in eligibility_lower or "crore" in eligibility_lower:
                    if self.user_response.startup_turnover is not None:
                        return self.user_response.startup_turnover <= 100
                return self.user_response.business_type == "Startup"
        
        # Journalist
        if "journalist" in data_field_lower or "journalist" in eligibility_lower:
            if "experience" in eligibility_lower and self.user_response.journalism_experience_years is not None:
                import re
                exp_match = re.search(r'(\d+)\s*year', eligibility_lower)
                if exp_match:
                    required_years = int(exp_match.group(1))
                    return self.user_response.journalism_experience_years >= required_years
            return self.user_response.is_journalist == True
        
        # Fisherman
        if "fisher" in data_field_lower or "fishermen" in eligibility_lower:
            if "cooperative" in eligibility_lower:
                return self.user_response.fisher_cooperative_member == True
            return self.user_response.occupation == "Fisherman" or self.user_response.is_fisherman == True
        
        # Unorganized sector worker
        if "unorganized" in data_field_lower or "craftsman" in eligibility_lower:
            return self.user_response.is_unorganized_worker == True
        
        # Pregnant/Lactating
        if "pregnant" in eligibility_lower or "lactating" in eligibility_lower or "nursing" in eligibility_lower:
            if "institutional delivery" in eligibility_lower:
                return self.user_response.willing_institutional_delivery == True
            return self.user_response.is_pregnant_or_lactating == True
        
        # Death related
        if "death" in data_field_lower or "deceased" in eligibility_lower:
            if "legal heir" in eligibility_lower or "dependent" in eligibility_lower:
                return self.user_response.is_legal_heir_or_dependent == True
            if "bbocwwb" in eligibility_lower:
                return self.user_response.deceased_was_bbocwwb_registered == True
            return self.user_response.applying_for_death_benefit == True
        
        # Pension
        if "pension" in data_field_lower or "pension" in eligibility_lower:
            if "not receiving" in eligibility_lower:
                return self.user_response.receiving_other_govt_pension == False
            return True
        
        # Rural area
        if "rural" in data_field_lower or "rural" in eligibility_lower:
            return self.user_response.belong_to_rural_area == True
        
        # Hostel
        if "hostel" in data_field_lower or "hostel" in eligibility_lower:
            if "minority" in eligibility_lower:
                return self.user_response.hostel_type == "Minority Welfare Hostel"
            if "sc/st" in eligibility_lower:
                return self.user_response.hostel_type == "SC/ST Welfare Hostel"
            if "government" in eligibility_lower:
                return self.user_response.hostel_type == "Government Hostel"
            return self.user_response.residing_in_hostel == True
        
        # Employment
        if "employment" in data_field_lower or "employee" in eligibility_lower:
            if "not employed" in eligibility_lower or "not a government" in eligibility_lower:
                return self.user_response.employment_status not in ["Government Employee", "PSU Employee"]
            if "retired" in eligibility_lower:
                return self.user_response.is_retired_govt_employee == True
        
        # Girl child
        if "girl child" in data_field_lower or "girl child" in eligibility_lower:
            if self.user_response.num_girl_children is not None:
                if "maximum" in eligibility_lower or "2" in eligibility_lower:
                    return self.user_response.num_girl_children <= 2 and self.user_response.num_girl_children > 0
                return self.user_response.num_girl_children > 0
            return self.user_response.gender == "Female"
        
        # Birth registered
        if "birth registered" in eligibility_lower:
            return self.user_response.birth_registered == True
        
        # Aadhaar
        if "aadhaar" in data_field_lower or "aadhaar" in eligibility_lower:
            if "bank account" in eligibility_lower or "linked" in eligibility_lower:
                return self.user_response.bank_account_linked_aadhaar == True
            return self.user_response.has_aadhaar == True
        
        # Medical conditions
        if "medical" in data_field_lower or "cancer" in eligibility_lower or "aids" in eligibility_lower:
            return self.user_response.has_medical_condition == True
        
        # Training
        if "training" in data_field_lower or "training" in eligibility_lower:
            if "skill" in eligibility_lower:
                return self.user_response.completed_skill_training == True
            if "departmental" in eligibility_lower:
                return self.user_response.completed_departmental_training == True
        
        # Previous benefit
        if "already received" in eligibility_lower or "availed" in eligibility_lower or "benefit earlier" in eligibility_lower:
            if "not" in eligibility_lower:
                return self.user_response.received_benefit_earlier == False
            return self.user_response.received_benefit_earlier == True
        
        # PMAY-G
        if "pmay-g" in eligibility_lower or "pmay" in eligibility_lower:
            return self.user_response.pmay_g_beneficiary == True
        
        # Driving license
        if "driving license" in eligibility_lower:
            return self.user_response.has_driving_license == True
        
        # Crop damage
        if "crop damage" in eligibility_lower:
            if self.user_response.crop_damage_percent is not None:
                if "33%" in eligibility_lower or "33" in eligibility_lower:
                    return self.user_response.crop_damage_percent >= 33
                return self.user_response.crop_damage_percent > 0
            return False
        
        # Milk producer
        if "milk" in eligibility_lower or "cattle" in eligibility_lower:
            if "cattle" in eligibility_lower and "healthy" in eligibility_lower:
                return self.user_response.cattle_certified_healthy == True
            return self.user_response.milk_producer_coop_member == True
        
        # Landless and houseless
        if "landless" in eligibility_lower and "houseless" in eligibility_lower:
            return self.user_response.landless_houseless == True
        
        # Default: If we can't parse, assume eligible (don't block)
        return True
    
    def _get_field_mapping(self) -> Dict[str, str]:
        """Get mapping from data field keywords to user response attributes."""
        return {
            "state_bihar": "state_bihar",
            "age": "age",
            "gender": "gender",
            "belong to": "category",
            "bpl": "is_bpl",
            "income": "annual_income",
            "land": "land_owned_acres",
            "farmer": "is_farmer",
            "dbt": "dbt_registered",
            "construction": "is_construction_worker",
            "bbocwwb": "bbocwwb_registered",
            "student": "is_student",
            "education": "education_level",
            "disability": "has_disability",
            "marital": "marital_status",
            "minority": "category",
            "business": "is_business_owner",
            "startup": "business_type",
            "journalist": "is_journalist",
            "fisher": "is_fisherman",
            "unorganized": "is_unorganized_worker",
            "pregnant": "is_pregnant_or_lactating",
            "death": "applying_for_death_benefit",
            "pension": "receiving_pension",
            "hostel": "residing_in_hostel",
            "employment": "employment_status"
        }


def run_cli_questionnaire():
    """Run the questionnaire in CLI mode."""
    questionnaire = SchemeQuestionnaire()
    
    print("\n" + "="*70)
    print("     BIHAR GOVERNMENT SCHEME FINDER")
    print("     Find schemes you are eligible for")
    print("="*70 + "\n")
    
    questions = questionnaire.get_all_questions()
    sections = questionnaire.get_sections()
    
    for section in sections:
        section_questions = [q for q in questions if q.get("section") == section]
        if not section_questions:
            continue
            
        print(f"\n{'─'*70}")
        print(f"  {section.upper()}")
        print(f"{'─'*70}\n")
        
        for q in section_questions:
            # Check conditions
            condition = q.get("condition")
            if condition and not _evaluate_condition(questionnaire, condition):
                continue
            
            answer = _ask_question(q)
            if answer is not None:
                questionnaire.set_response(q["id"], answer)
    
    # Find eligible schemes
    print("\n" + "="*70)
    print("  ANALYZING YOUR ELIGIBILITY...")
    print("="*70 + "\n")
    
    eligible_schemes = questionnaire.find_eligible_schemes()
    
    if eligible_schemes:
        print(f"✅ You are eligible for {len(eligible_schemes)} scheme(s):\n")
        for i, scheme in enumerate(eligible_schemes, 1):
            print(f"{i}. {scheme['name']}")
            print(f"   Match: {scheme['matched_criteria']}/{scheme['total_criteria']} criteria ({scheme['match_percentage']:.0f}%)")
            print()
    else:
        print("❌ No exact matches found based on your responses.")
        print("   Try adjusting your answers or check individual scheme requirements.")
    
    return eligible_schemes


def _evaluate_condition(questionnaire: SchemeQuestionnaire, condition: str) -> bool:
    """Evaluate a condition string."""
    try:
        # Simple condition parsing
        if "==" in condition:
            parts = condition.split("==")
            field = parts[0].strip()
            value = parts[1].strip().strip("'\"")
            
            actual_value = questionnaire.get_response(field)
            
            if value == "True":
                return actual_value == True
            elif value == "False":
                return actual_value == False
            else:
                return str(actual_value) == value
        
        if ">" in condition:
            parts = condition.split(">")
            field = parts[0].strip()
            value = int(parts[1].strip())
            
            actual_value = questionnaire.get_response(field)
            return actual_value is not None and actual_value > value
        
        return True
    except:
        return True


def _ask_question(q: Dict) -> Any:
    """Ask a single question and get user input."""
    question_text = q["question"]
    q_type = q.get("type", "text")
    
    print(f"Q: {question_text}")
    
    if q_type == "boolean":
        while True:
            answer = input("   Enter (yes/no): ").strip().lower()
            if answer in ["yes", "y", "1", "true"]:
                return True
            elif answer in ["no", "n", "0", "false"]:
                return False
            elif answer == "":
                return None
            print("   Please enter 'yes' or 'no'")
    
    elif q_type == "number":
        while True:
            answer = input("   Enter number: ").strip()
            if answer == "":
                return None
            try:
                num = float(answer)
                if "min" in q and num < q["min"]:
                    print(f"   Value must be at least {q['min']}")
                    continue
                if "max" in q and num > q["max"]:
                    print(f"   Value must be at most {q['max']}")
                    continue
                return int(num) if num == int(num) else num
            except ValueError:
                print("   Please enter a valid number")
    
    elif q_type == "choice":
        options = q.get("options", [])
        for i, opt in enumerate(options, 1):
            print(f"   {i}. {opt}")
        while True:
            answer = input("   Enter choice number: ").strip()
            if answer == "":
                return None
            try:
                idx = int(answer) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                print(f"   Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("   Please enter a valid number")
    
    else:  # text
        answer = input("   Enter: ").strip()
        return answer if answer else None


if __name__ == "__main__":
    run_cli_questionnaire()
