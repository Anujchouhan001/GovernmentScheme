"""
Data models for Scheme Finder application.
Defines the structure for Scheme and User Profile.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json


@dataclass
class Scheme:
    """
    Represents a government scheme with all its details and eligibility criteria.
    """
    scheme_name: str
    state_name: str
    scheme_url: str
    details: str
    benefits: List[str]
    eligibility: List[str]
    application_process: List[str]
    documents_required: List[str]
    faqs: List[Dict[str, str]]
    
    # Parsed eligibility criteria
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: Optional[str] = None  # Male, Female, Transgender, All
    categories: List[str] = field(default_factory=list)  # SC, ST, BC, EBC, General, EWS
    occupation: List[str] = field(default_factory=list)  # Farmer, Student, Worker, etc.
    max_income: Optional[float] = None
    required_state: Optional[str] = None
    required_districts: List[str] = field(default_factory=list)
    is_bpl: Optional[bool] = None
    is_disability: Optional[bool] = None
    education_level: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Parse eligibility criteria after initialization."""
        self._parse_eligibility()
        self._extract_keywords()
    
    def _parse_eligibility(self):
        """Extract structured eligibility criteria from text."""
        eligibility_text = " ".join(self.eligibility).lower()
        
        # Parse age
        import re
        age_pattern = r'(\d+)\s*(?:and|to|-)\s*(\d+)\s*years?'
        age_match = re.search(age_pattern, eligibility_text)
        if age_match:
            self.min_age = int(age_match.group(1))
            self.max_age = int(age_match.group(2))
        
        # Parse gender - check for specific gender-only mentions
        # Look for patterns like "female only", "female applicants", "women only"
        if re.search(r'\b(female\s*(only|applicants?)|women\s*only|for\s*women|widow)\b', eligibility_text):
            self.gender = 'Female'
        elif re.search(r'\bmale\s*(only|applicants?)\b', eligibility_text):
            self.gender = 'Male'
        else:
            self.gender = 'All'
        
        # Parse categories
        category_mapping = {
            'scheduled caste': 'SC',
            'scheduled tribe': 'ST',
            'backward class': 'BC',
            'extremely backward': 'EBC',
            'general': 'General',
            'ews': 'EWS',
            'economically weaker section': 'EWS'
        }
        
        for key, value in category_mapping.items():
            if key in eligibility_text:
                if value not in self.categories:
                    self.categories.append(value)
        
        # Parse occupation
        occupation_keywords = {
            'farmer': 'Farmer',
            'student': 'Student',
            'worker': 'Worker',
            'construction worker': 'Construction Worker',
            'entrepreneur': 'Entrepreneur',
            'business': 'Entrepreneur',
            'fisherman': 'Fisherman',
            'artisan': 'Artisan',
            'craftsman': 'Artisan'
        }
        
        for key, value in occupation_keywords.items():
            if key in eligibility_text:
                if value not in self.occupation:
                    self.occupation.append(value)
        
        # Parse income
        income_pattern = r'₹\s*(\d+(?:,\d+)*)'
        income_matches = re.findall(income_pattern, eligibility_text)
        if income_matches:
            # Take the first income mentioned as max income
            income_str = income_matches[0].replace(',', '')
            self.max_income = float(income_str)
        
        # Parse state
        if 'bihar' in eligibility_text:
            self.required_state = 'Bihar'
        
        # Parse BPL
        if 'below poverty line' in eligibility_text or 'bpl' in eligibility_text:
            self.is_bpl = True
        
        # Parse disability
        if 'disability' in eligibility_text or 'divyangjan' in eligibility_text:
            self.is_disability = True
        
        # Parse education
        education_keywords = ['10th', '12th', 'graduate', 'post-graduate', 'iti', 'polytechnic', 'diploma']
        for edu in education_keywords:
            if edu in eligibility_text:
                self.education_level.append(edu.title())
    
    def _extract_keywords(self):
        """Extract keywords for matching from scheme name and details."""
        combined_text = f"{self.scheme_name} {self.details}".lower()
        
        keyword_list = [
            'kisan', 'krishi', 'farmer', 'agriculture', 'horticulture',
            'student', 'scholarship', 'education', 'school',
            'women', 'female', 'girl', 'widow',
            'divyangjan', 'disability', 'handicapped',
            'startup', 'entrepreneur', 'business',
            'pension', 'welfare', 'social security',
            'marriage', 'vivah',
            'fisheries', 'matsya', 'fish'
        ]
        
        for keyword in keyword_list:
            if keyword in combined_text:
                if keyword not in self.keywords:
                    self.keywords.append(keyword)
    
    def calculate_match_score(self, user_profile: 'UserProfile') -> tuple[float, List[str]]:
        """
        Calculate how well this scheme matches the user profile.
        Returns (score, reasons) tuple.
        """
        score = 0.0
        reasons = []
        
        # Age check (20 points)
        if self.min_age is not None and self.max_age is not None:
            if self.min_age <= user_profile.age <= self.max_age:
                score += 20
                reasons.append(f"Age {user_profile.age} is within range {self.min_age}-{self.max_age}")
            else:
                return 0.0, ["Age not eligible"]
        
        # Gender check (15 points)
        if self.gender and self.gender != 'All':
            if self.gender == user_profile.gender:
                score += 15
                reasons.append(f"Gender matches: {user_profile.gender}")
            else:
                return 0.0, [f"Gender mismatch: Scheme requires {self.gender}"]
        else:
            score += 10  # Partial points for gender-neutral schemes
        
        # Category check (15 points)
        if self.categories:
            if user_profile.category in self.categories:
                score += 15
                reasons.append(f"Category matches: {user_profile.category}")
            else:
                # Not a hard rejection if multiple categories allowed
                if len(self.categories) > 3:  # Scheme accepts multiple categories
                    score += 5
        else:
            score += 10  # No category restriction
        
        # Occupation check (15 points)
        if self.occupation:
            if user_profile.occupation in self.occupation:
                score += 15
                reasons.append(f"Occupation matches: {user_profile.occupation}")
            else:
                # Check if occupation keywords match
                occupation_match = False
                for occ in self.occupation:
                    if occ.lower() in user_profile.occupation.lower():
                        score += 10
                        occupation_match = True
                        break
                if not occupation_match:
                    score += 2  # Small penalty but don't disqualify
        else:
            score += 10
        
        # Income check (10 points)
        if self.max_income is not None:
            if user_profile.annual_income <= self.max_income:
                score += 10
                reasons.append(f"Income ₹{user_profile.annual_income} is within limit ₹{self.max_income}")
            else:
                return 0.0, [f"Income ₹{user_profile.annual_income} exceeds limit ₹{self.max_income}"]
        else:
            score += 5
        
        # BPL check (10 points)
        if self.is_bpl is not None:
            if self.is_bpl == user_profile.is_bpl:
                score += 10
                if user_profile.is_bpl:
                    reasons.append("BPL status matches")
            elif self.is_bpl and not user_profile.is_bpl:
                return 0.0, ["Scheme requires BPL status"]
        else:
            score += 5
        
        # Disability check (10 points)
        if self.is_disability is not None:
            if self.is_disability == user_profile.has_disability:
                score += 10
                if user_profile.has_disability:
                    reasons.append("Disability status matches")
            elif self.is_disability and not user_profile.has_disability:
                return 0.0, ["Scheme requires disability certificate"]
        else:
            score += 5
        
        # Keyword match (5 points)
        keyword_matches = 0
        for keyword in self.keywords:
            if keyword in user_profile.occupation.lower():
                keyword_matches += 1
        if keyword_matches > 0:
            score += min(5, keyword_matches * 2)
            reasons.append(f"Matched {keyword_matches} keywords")
        
        return score, reasons


@dataclass
class UserProfile:
    """
    Represents a user's profile with all information needed for scheme matching.
    """
    # Basic Demographics
    state: str = "Bihar"
    age: int = 0
    gender: str = ""  # Male, Female, Transgender
    category: str = ""  # General, EWS, BC, EBC, SC, ST
    
    # Professional/Occupational
    occupation: str = ""
    owns_agricultural_land: bool = False
    land_size_acres: float = 0.0
    is_registered_worker: bool = False
    business_type: str = ""  # Startup, Proprietorship, Partnership
    
    # Educational
    education_level: str = ""
    cleared_competitive_exam: bool = False
    
    # Financial & Social
    annual_income: float = 0.0
    is_bpl: bool = False
    has_disability: bool = False
    marital_status: str = ""  # Single, Married, Widow
    
    # Location
    district: str = ""
    
    # Infrastructure
    has_water_body_access: bool = False
    water_body_type: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user profile to dictionary."""
        return {
            'state': self.state,
            'age': self.age,
            'gender': self.gender,
            'category': self.category,
            'occupation': self.occupation,
            'owns_agricultural_land': self.owns_agricultural_land,
            'land_size_acres': self.land_size_acres,
            'is_registered_worker': self.is_registered_worker,
            'business_type': self.business_type,
            'education_level': self.education_level,
            'cleared_competitive_exam': self.cleared_competitive_exam,
            'annual_income': self.annual_income,
            'is_bpl': self.is_bpl,
            'has_disability': self.has_disability,
            'marital_status': self.marital_status,
            'district': self.district,
            'has_water_body_access': self.has_water_body_access,
            'water_body_type': self.water_body_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create UserProfile from dictionary."""
        return cls(**data)
