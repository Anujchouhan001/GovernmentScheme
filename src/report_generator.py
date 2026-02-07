"""
Report Generator - Generates formatted reports of scheme recommendations.
"""

from typing import List, Tuple
from src.models import Scheme, UserProfile
from datetime import datetime


class ReportGenerator:
    """
    Generates formatted reports for scheme recommendations.
    """
    
    @staticmethod
    def generate_console_report(
        user_profile: UserProfile,
        eligible_schemes: List[Tuple[Scheme, float, List[str]]],
        show_details: bool = False
    ) -> str:
        """
        Generate a formatted console report.
        
        Args:
            user_profile: User's profile
            eligible_schemes: List of (scheme, score, reasons) tuples
            show_details: Whether to show full scheme details
            
        Returns:
            Formatted report string
        """
        report = []
        
        # Header
        report.append("\n" + "="*80)
        report.append("         SCHEME RECOMMENDATION REPORT")
        report.append("="*80)
        
        # User Summary
        report.append("\n📋 USER PROFILE SUMMARY")
        report.append("─" * 80)
        report.append(f"Age: {user_profile.age} years")
        report.append(f"Gender: {user_profile.gender}")
        report.append(f"Category: {user_profile.category}")
        report.append(f"Occupation: {user_profile.occupation}")
        report.append(f"Annual Income: ₹{user_profile.annual_income:,.0f}")
        report.append(f"District: {user_profile.district}")
        
        # Results Summary
        report.append(f"\n🎯 FOUND {len(eligible_schemes)} ELIGIBLE SCHEMES")
        report.append("="*80)
        
        if not eligible_schemes:
            report.append("\n❌ No schemes found matching your profile.")
            report.append("   Try updating your information or check back later for new schemes.")
            return "\n".join(report)
        
        # List schemes
        for idx, (scheme, score, reasons) in enumerate(eligible_schemes, 1):
            report.append(f"\n{'─'*80}")
            report.append(f"#{idx}. {scheme.scheme_name}")
            report.append(f"{'─'*80}")
            report.append(f"Match Score: {score:.1f}/100  {'🌟' * min(5, int(score/20))}")
            report.append(f"State: {scheme.state_name}")
            
            # Eligibility reasons
            if reasons:
                report.append(f"\n✓ Why you're eligible:")
                for reason in reasons[:3]:  # Show top 3 reasons
                    report.append(f"  • {reason}")
            
            # Benefits (first 2)
            if scheme.benefits:
                report.append(f"\n💰 Key Benefits:")
                for benefit in scheme.benefits[:2]:
                    # Clean up benefit text
                    benefit_text = benefit.strip().replace('""', '').strip('"')
                    if len(benefit_text) > 100:
                        benefit_text = benefit_text[:97] + "..."
                    report.append(f"  • {benefit_text}")
            
            # Basic eligibility (first 3 criteria)
            if show_details and scheme.eligibility:
                report.append(f"\n📌 Eligibility Criteria:")
                for criteria in scheme.eligibility[:3]:
                    criteria_text = criteria.strip().replace('""', '').strip('"')
                    if len(criteria_text) > 100:
                        criteria_text = criteria_text[:97] + "..."
                    report.append(f"  • {criteria_text}")
            
            # URL
            report.append(f"\n🔗 More Info: {scheme.scheme_url}")
            
            if idx < len(eligible_schemes):
                report.append("")
        
        # Footer
        report.append("\n" + "="*80)
        report.append(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*80)
        
        return "\n".join(report)
    
    @staticmethod
    def generate_detailed_scheme_report(scheme: Scheme) -> str:
        """
        Generate a detailed report for a single scheme.
        
        Args:
            scheme: The scheme to generate report for
            
        Returns:
            Detailed scheme report
        """
        report = []
        
        report.append("\n" + "="*80)
        report.append(f"  {scheme.scheme_name}")
        report.append("="*80)
        
        # Basic Info
        report.append(f"\n📍 State: {scheme.state_name}")
        report.append(f"🔗 Official URL: {scheme.scheme_url}")
        
        # Details
        report.append(f"\n📖 SCHEME DETAILS")
        report.append("─" * 80)
        report.append(scheme.details)
        
        # Benefits
        if scheme.benefits:
            report.append(f"\n💰 BENEFITS")
            report.append("─" * 80)
            for i, benefit in enumerate(scheme.benefits, 1):
                benefit_text = benefit.strip().replace('""', '').strip('"')
                report.append(f"{i}. {benefit_text}")
        
        # Eligibility
        if scheme.eligibility:
            report.append(f"\n✅ ELIGIBILITY CRITERIA")
            report.append("─" * 80)
            for i, criteria in enumerate(scheme.eligibility, 1):
                criteria_text = criteria.strip().replace('""', '').strip('"')
                report.append(f"{i}. {criteria_text}")
        
        # Documents Required
        if scheme.documents_required:
            report.append(f"\n📄 DOCUMENTS REQUIRED")
            report.append("─" * 80)
            for i, doc in enumerate(scheme.documents_required, 1):
                doc_text = doc.strip().replace('""', '').strip('"')
                report.append(f"{i}. {doc_text}")
        
        # Application Process (first 5 steps)
        if scheme.application_process:
            report.append(f"\n📝 APPLICATION PROCESS (First 5 Steps)")
            report.append("─" * 80)
            for i, step in enumerate(scheme.application_process[:5], 1):
                step_text = step.strip().replace('""', '').strip('"')
                report.append(f"{i}. {step_text}")
        
        # FAQs (first 3)
        if scheme.faqs:
            report.append(f"\n❓ FREQUENTLY ASKED QUESTIONS (Top 3)")
            report.append("─" * 80)
            for i, faq in enumerate(scheme.faqs[:3], 1):
                report.append(f"\nQ{i}: {faq.get('question', 'N/A')}")
                report.append(f"A{i}: {faq.get('answer', 'N/A')}")
        
        report.append("\n" + "="*80)
        
        return "\n".join(report)
    
    @staticmethod
    def save_to_file(content: str, filename: str = None):
        """
        Save report to a text file.
        
        Args:
            content: Report content
            filename: Output filename (auto-generated if not provided)
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"scheme_report_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n✓ Report saved to: {filename}")
        except Exception as e:
            print(f"\n✗ Error saving report: {e}")
