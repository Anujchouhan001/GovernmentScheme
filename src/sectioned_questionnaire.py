"""
Section-based Conditional Questionnaire System
Questions are organized in sections (A, B, C, etc.)
Each section must be satisfied before moving to the next
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class SectionStatus(Enum):
    """Status of a questionnaire section"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


@dataclass
class Question:
    """Individual question in a section"""
    id: str
    text: str
    type: str  # text, number, yes_no, select, multi_select
    required: bool = True
    options: List[str] = field(default_factory=list)
    condition: Optional[Dict[str, Any]] = None  # Condition to show this question
    

@dataclass
class Section:
    """A section of related questions"""
    id: str
    name: str
    description: str
    order: int
    questions: List[Question] = field(default_factory=list)
    conditions: List[Dict[str, Any]] = field(default_factory=list)  # Conditions to unlock this section
    status: SectionStatus = SectionStatus.NOT_STARTED
    

class SectionedQuestionnaire:
    """
    Manages a section-based questionnaire where sections are
    unlocked conditionally based on previous answers
    """
    
    def __init__(self):
        self.sections: List[Section] = []
        self.user_responses: Dict[str, Any] = {}
        self.current_section_id: Optional[str] = None
        self._load_sections()
        
    def _load_sections(self):
        """Load questionnaire sections from configuration"""
        # Section A: Basic Demographics
        section_a = Section(
            id="section_a",
            name="Section A: Basic Information",
            description="Let's start with some basic information about you",
            order=1,
            questions=[
                Question(
                    id="state",
                    text="Which state do you live in?",
                    type="select",
                    options=["Bihar", "Other"]
                ),
                Question(
                    id="age",
                    text="What is your age?",
                    type="number"
                ),
                Question(
                    id="gender",
                    text="What is your gender?",
                    type="select",
                    options=["Male", "Female", "Transgender", "Other"]
                ),
                Question(
                    id="category",
                    text="Which social category do you belong to?",
                    type="select",
                    options=["General", "OBC (Other Backward Class)", "EBC (Extremely Backward Class)", 
                            "SC (Scheduled Caste)", "ST (Scheduled Tribe)", "Minority"]
                ),
            ]
        )
        
        # Section B: Economic Status
        section_b = Section(
            id="section_b",
            name="Section B: Economic Status",
            description="Now let's understand your economic situation",
            order=2,
            conditions=[
                {"field": "state", "operator": "equals", "value": "Bihar"}
            ],
            questions=[
                Question(
                    id="annual_income",
                    text="What is your annual family income (in Rupees)?",
                    type="number"
                ),
                Question(
                    id="is_bpl",
                    text="Do you have a BPL (Below Poverty Line) card?",
                    type="yes_no"
                ),
                Question(
                    id="is_ultra_poor",
                    text="Do you belong to ultra-poor category?",
                    type="yes_no"
                ),
                Question(
                    id="belong_to_rural_area",
                    text="Do you live in a rural area?",
                    type="yes_no"
                ),
            ]
        )
        
        # Section C: Occupation
        section_c = Section(
            id="section_c",
            name="Section C: Occupation & Employment",
            description="Tell us about your work and occupation",
            order=3,
            conditions=[
                {"field": "age", "operator": ">=", "value": 18}
            ],
            questions=[
                Question(
                    id="occupation",
                    text="What is your primary occupation?",
                    type="select",
                    options=["Farmer", "Construction Worker", "Student", "Business Owner", 
                            "Government Employee", "Private Employee", "Self-Employed", 
                            "Unemployed", "Retired", "Other"]
                ),
                Question(
                    id="is_farmer",
                    text="Are you a farmer?",
                    type="yes_no",
                    condition={"field": "occupation", "operator": "not_equals", "value": "Farmer"}
                ),
                Question(
                    id="is_construction_worker",
                    text="Are you a construction worker?",
                    type="yes_no",
                    condition={"field": "occupation", "operator": "not_equals", "value": "Construction Worker"}
                ),
                Question(
                    id="is_student",
                    text="Are you currently a student?",
                    type="yes_no",
                    condition={"field": "occupation", "operator": "not_equals", "value": "Student"}
                ),
            ]
        )
        
        # Section D: Land & Property
        section_d = Section(
            id="section_d",
            name="Section D: Land & Property",
            description="Information about land ownership and property",
            order=4,
            conditions=[
                {"any": [
                    {"field": "is_farmer", "operator": "equals", "value": True},
                    {"field": "occupation", "operator": "equals", "value": "Farmer"}
                ]}
            ],
            questions=[
                Question(
                    id="land_owned_acres",
                    text="How much land do you own (in acres)?",
                    type="number"
                ),
                Question(
                    id="owns_house",
                    text="Do you own a house?",
                    type="yes_no"
                ),
                Question(
                    id="landless_houseless",
                    text="Are you landless and houseless?",
                    type="yes_no"
                ),
            ]
        )
        
        # Section E: Farmer Specific
        section_e = Section(
            id="section_e",
            name="Section E: Farmer Details",
            description="Additional information for farmers",
            order=5,
            conditions=[
                {"field": "is_farmer", "operator": "equals", "value": True}
            ],
            questions=[
                Question(
                    id="dbt_registered",
                    text="Are you registered on DBT (Direct Benefit Transfer) portal?",
                    type="yes_no"
                ),
                Question(
                    id="crop_damage_percent",
                    text="Have you experienced crop damage? If yes, what percentage?",
                    type="number"
                ),
            ]
        )
        
        # Section F: Construction Worker Specific
        section_f = Section(
            id="section_f",
            name="Section F: Construction Worker Details",
            description="Additional information for construction workers",
            order=6,
            conditions=[
                {"field": "is_construction_worker", "operator": "equals", "value": True}
            ],
            questions=[
                Question(
                    id="bbocwwb_registered",
                    text="Are you registered with Bihar Building & Other Construction Workers Welfare Board (BBOCWWB)?",
                    type="yes_no"
                ),
                Question(
                    id="bbocwwb_membership_years",
                    text="If registered, how many years of membership do you have?",
                    type="number",
                    required=False
                ),
                Question(
                    id="bbocwwb_active_membership",
                    text="Is your BBOCWWB membership currently active?",
                    type="yes_no",
                    required=False
                ),
            ]
        )
        
        # Section G: Student Specific
        section_g = Section(
            id="section_g",
            name="Section G: Education Details",
            description="Information about your education",
            order=7,
            conditions=[
                {"field": "is_student", "operator": "equals", "value": True}
            ],
            questions=[
                Question(
                    id="education_level",
                    text="What is your current education level?",
                    type="select",
                    options=["Primary (1-5)", "Middle (6-8)", "Secondary (9-10)", 
                            "Higher Secondary (11-12)", "Undergraduate", "Postgraduate", "Doctorate"]
                ),
                Question(
                    id="passed_10th_first_division",
                    text="Have you passed 10th with first division?",
                    type="yes_no",
                    required=False
                ),
                Question(
                    id="passed_12th",
                    text="Have you passed 12th?",
                    type="yes_no",
                    required=False
                ),
            ]
        )
        
        # Section H: Family Information
        section_h = Section(
            id="section_h",
            name="Section H: Family Information",
            description="Details about your family",
            order=8,
            questions=[
                Question(
                    id="marital_status",
                    text="What is your marital status?",
                    type="select",
                    options=["Unmarried", "Married", "Divorced", "Widowed", "Abandoned", "Remarried"]
                ),
                Question(
                    id="num_children",
                    text="How many children do you have?",
                    type="number",
                    required=False,
                    condition={"field": "marital_status", "operator": "in", "value": ["Married", "Divorced", "Widowed", "Abandoned", "Remarried"]}
                ),
                Question(
                    id="num_girl_children",
                    text="How many girl children do you have?",
                    type="number",
                    required=False,
                    condition={"field": "marital_status", "operator": "in", "value": ["Married", "Divorced", "Widowed", "Abandoned", "Remarried"]}
                ),
            ]
        )
        
        # Section I: Identity & Documentation
        section_i = Section(
            id="section_i",
            name="Section I: Identity Documents",
            description="Information about your identity documents",
            order=9,
            questions=[
                Question(
                    id="has_aadhaar",
                    text="Do you have an Aadhaar card?",
                    type="yes_no"
                ),
                Question(
                    id="bank_account_linked_aadhaar",
                    text="Is your bank account linked with Aadhaar?",
                    type="yes_no"
                ),
            ]
        )
        
        # Section J: Health & Disability
        section_j = Section(
            id="section_j",
            name="Section J: Health & Disability",
            description="Health and disability related information",
            order=10,
            questions=[
                Question(
                    id="has_disability",
                    text="Do you have any disability?",
                    type="yes_no"
                ),
                Question(
                    id="disability_percentage",
                    text="If yes, what is the disability percentage?",
                    type="number",
                    required=False,
                    condition={"field": "has_disability", "operator": "equals", "value": True}
                ),
                Question(
                    id="has_medical_condition",
                    text="Do you have any chronic medical condition?",
                    type="yes_no"
                ),
            ]
        )
        
        # Add all sections
        self.sections = [
            section_a, section_b, section_c, section_d, section_e,
            section_f, section_g, section_h, section_i, section_j
        ]
        
        # Sort by order
        self.sections.sort(key=lambda s: s.order)
        
        # Mark first section as current
        if self.sections:
            self.sections[0].status = SectionStatus.IN_PROGRESS
            self.current_section_id = self.sections[0].id
    
    def get_current_section(self) -> Optional[Section]:
        """Get the current active section"""
        for section in self.sections:
            if section.id == self.current_section_id:
                return section
        return None
    
    def get_section_by_id(self, section_id: str) -> Optional[Section]:
        """Get a section by its ID"""
        for section in self.sections:
            if section.id == section_id:
                return section
        return None
    
    def check_section_condition(self, section: Section) -> bool:
        """Check if a section's conditions are satisfied"""
        if not section.conditions:
            return True
            
        for condition in section.conditions:
            if "any" in condition:
                # At least one sub-condition must be true
                any_satisfied = False
                for sub_cond in condition["any"]:
                    if self._evaluate_condition(sub_cond):
                        any_satisfied = True
                        break
                if not any_satisfied:
                    return False
            elif "all" in condition:
                # All sub-conditions must be true
                for sub_cond in condition["all"]:
                    if not self._evaluate_condition(sub_cond):
                        return False
            else:
                # Single condition
                if not self._evaluate_condition(condition):
                    return False
        
        return True
    
    def _evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        
        if field not in self.user_responses:
            return False
        
        user_value = self.user_responses[field]
        
        if operator == "equals":
            return user_value == value
        elif operator == "!=":
            return user_value != value
        elif operator == ">":
            return user_value > value
        elif operator == ">=":
            return user_value >= value
        elif operator == "<":
            return user_value < value
        elif operator == "<=":
            return user_value <= value
        elif operator == "in":
            return user_value in value
        elif operator == "not_in":
            return user_value not in value
        
        return False
    
    def save_response(self, question_id: str, answer: Any):
        """Save a user's response"""
        self.user_responses[question_id] = answer
    
    def is_section_complete(self, section: Section) -> bool:
        """Check if all required questions in a section are answered"""
        for question in section.questions:
            # Skip if question has a condition and it's not met
            if question.condition and not self._evaluate_condition(question.condition):
                continue
                
            if question.required and question.id not in self.user_responses:
                return False
        
        return True
    
    def get_next_section(self) -> Optional[Section]:
        """Get the next available section based on conditions"""
        current_section = self.get_current_section()
        if not current_section:
            return None
        
        current_index = self.sections.index(current_section)
        
        # Check all subsequent sections
        for i in range(current_index + 1, len(self.sections)):
            section = self.sections[i]
            if self.check_section_condition(section):
                return section
        
        return None
    
    def move_to_next_section(self) -> bool:
        """Move to the next section if current is complete"""
        current_section = self.get_current_section()
        if not current_section or not self.is_section_complete(current_section):
            return False
        
        # Mark current as completed
        current_section.status = SectionStatus.COMPLETED
        
        # Get and activate next section
        next_section = self.get_next_section()
        if next_section:
            next_section.status = SectionStatus.IN_PROGRESS
            self.current_section_id = next_section.id
            return True
        
        return False
    
    def get_progress(self) -> Dict[str, Any]:
        """Get questionnaire progress"""
        total = len(self.sections)
        completed = sum(1 for s in self.sections if s.status == SectionStatus.COMPLETED)
        current = self.get_current_section()
        
        return {
            "total_sections": total,
            "completed_sections": completed,
            "current_section": current.name if current else None,
            "progress_percentage": int((completed / total) * 100) if total > 0 else 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Export questionnaire state as dictionary"""
        return {
            "sections": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "order": s.order,
                    "status": s.status.value,
                    "questions": [
                        {
                            "id": q.id,
                            "text": q.text,
                            "type": q.type,
                            "required": q.required,
                            "options": q.options,
                            "condition": q.condition
                        }
                        for q in s.questions
                    ]
                }
                for s in self.sections
            ],
            "current_section_id": self.current_section_id,
            "user_responses": self.user_responses,
            "progress": self.get_progress()
        }
