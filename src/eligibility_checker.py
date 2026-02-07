"""
Eligibility Checker - Matches user profiles with schemes based on eligibility criteria.
"""

from typing import List, Tuple
from src.models import Scheme, UserProfile


class EligibilityChecker:
    """
    Checks user eligibility for schemes and provides ranked recommendations.
    """
    
    def __init__(self, schemes: List[Scheme]):
        """
        Initialize the eligibility checker.
        
        Args:
            schemes: List of all available schemes
        """
        self.schemes = schemes
    
    def find_eligible_schemes(
        self, 
        user_profile: UserProfile, 
        min_score: float = 50.0
    ) -> List[Tuple[Scheme, float, List[str]]]:
        """
        Find all schemes eligible for the user and rank them by match score.
        
        Args:
            user_profile: User's profile information
            min_score: Minimum score threshold (0-100)
            
        Returns:
            List of tuples: (scheme, score, reasons)
        """
        eligible_schemes = []
        
        for scheme in self.schemes:
            # Calculate match score
            score, reasons = scheme.calculate_match_score(user_profile)
            
            # Only include if score meets minimum threshold
            if score >= min_score:
                eligible_schemes.append((scheme, score, reasons))
        
        # Sort by score (highest first)
        eligible_schemes.sort(key=lambda x: x[1], reverse=True)
        
        return eligible_schemes
    
    def get_top_schemes(
        self, 
        user_profile: UserProfile, 
        limit: int = 10
    ) -> List[Tuple[Scheme, float, List[str]]]:
        """
        Get top N schemes for the user.
        
        Args:
            user_profile: User's profile information
            limit: Maximum number of schemes to return
            
        Returns:
            List of top matching schemes
        """
        all_eligible = self.find_eligible_schemes(user_profile, min_score=0)
        return all_eligible[:limit]
    
    def filter_by_category(
        self, 
        user_profile: UserProfile, 
        category: str
    ) -> List[Tuple[Scheme, float, List[str]]]:
        """
        Filter schemes by a specific category (e.g., education, agriculture).
        
        Args:
            user_profile: User's profile information
            category: Category keyword to filter by
            
        Returns:
            Filtered list of schemes
        """
        all_eligible = self.find_eligible_schemes(user_profile)
        category_lower = category.lower()
        
        filtered = [
            (scheme, score, reasons)
            for scheme, score, reasons in all_eligible
            if category_lower in scheme.scheme_name.lower() 
            or category_lower in scheme.details.lower()
            or category_lower in ' '.join(scheme.keywords).lower()
        ]
        
        return filtered
    
    def explain_ineligibility(self, scheme: Scheme, user_profile: UserProfile) -> List[str]:
        """
        Explain why a user is not eligible for a specific scheme.
        
        Args:
            scheme: The scheme to check
            user_profile: User's profile
            
        Returns:
            List of reasons for ineligibility
        """
        reasons = []
        
        # Age check
        if scheme.min_age is not None and scheme.max_age is not None:
            if not (scheme.min_age <= user_profile.age <= scheme.max_age):
                reasons.append(
                    f"Age requirement: {scheme.min_age}-{scheme.max_age} years "
                    f"(Your age: {user_profile.age})"
                )
        
        # Gender check
        if scheme.gender and scheme.gender != 'All':
            if scheme.gender != user_profile.gender:
                reasons.append(
                    f"Gender requirement: {scheme.gender} "
                    f"(Your gender: {user_profile.gender})"
                )
        
        # Category check
        if scheme.categories:
            if user_profile.category not in scheme.categories:
                reasons.append(
                    f"Category requirement: {', '.join(scheme.categories)} "
                    f"(Your category: {user_profile.category})"
                )
        
        # Income check
        if scheme.max_income is not None:
            if user_profile.annual_income > scheme.max_income:
                reasons.append(
                    f"Income limit: ₹{scheme.max_income} "
                    f"(Your income: ₹{user_profile.annual_income})"
                )
        
        # BPL check
        if scheme.is_bpl is not None:
            if scheme.is_bpl and not user_profile.is_bpl:
                reasons.append("BPL certificate required")
        
        # Disability check
        if scheme.is_disability is not None:
            if scheme.is_disability and not user_profile.has_disability:
                reasons.append("Disability certificate required")
        
        if not reasons:
            reasons.append("You may be eligible! Check detailed eligibility criteria.")
        
        return reasons
    
    def get_statistics(self) -> dict:
        """
        Get statistics about available schemes.
        
        Returns:
            Dictionary with scheme statistics
        """
        stats = {
            'total_schemes': len(self.schemes),
            'by_state': {},
            'by_category': {
                'SC': 0,
                'ST': 0,
                'BC': 0,
                'EBC': 0,
                'General': 0,
                'All': 0
            },
            'by_gender': {
                'Male': 0,
                'Female': 0,
                'All': 0
            },
            'with_age_limit': 0,
            'with_income_limit': 0,
            'for_disabled': 0,
            'for_bpl': 0
        }
        
        for scheme in self.schemes:
            # Count by state
            state = scheme.state_name
            stats['by_state'][state] = stats['by_state'].get(state, 0) + 1
            
            # Count by category
            if scheme.categories:
                for cat in scheme.categories:
                    if cat in stats['by_category']:
                        stats['by_category'][cat] += 1
            else:
                stats['by_category']['All'] += 1
            
            # Count by gender
            if scheme.gender:
                if scheme.gender in stats['by_gender']:
                    stats['by_gender'][scheme.gender] += 1
            
            # Count filters
            if scheme.min_age is not None:
                stats['with_age_limit'] += 1
            if scheme.max_income is not None:
                stats['with_income_limit'] += 1
            if scheme.is_disability:
                stats['for_disabled'] += 1
            if scheme.is_bpl:
                stats['for_bpl'] += 1
        
        return stats
