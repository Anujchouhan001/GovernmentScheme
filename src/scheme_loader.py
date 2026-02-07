"""
Scheme Loader - Loads schemes from CSV and parses them into Scheme objects.
"""

import csv
import json
from typing import List
from pathlib import Path
from src.models import Scheme


class SchemeLoader:
    """Loads and parses government schemes from CSV file."""
    
    def __init__(self, csv_path: str):
        """
        Initialize the scheme loader.
        
        Args:
            csv_path: Path to the CSV file containing scheme data
        """
        self.csv_path = Path(csv_path)
        self.schemes: List[Scheme] = []
    
    def load_schemes(self) -> List[Scheme]:
        """
        Load all schemes from CSV file.
        
        Returns:
            List of Scheme objects
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Scheme data file not found: {self.csv_path}")
        
        self.schemes = []
        
        with open(self.csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    scheme = self._parse_scheme_row(row)
                    self.schemes.append(scheme)
                except Exception as e:
                    print(f"Error parsing scheme '{row.get('scheme_name', 'Unknown')}': {e}")
                    continue
        
        print(f"✓ Loaded {len(self.schemes)} schemes from database")
        return self.schemes
    
    def _parse_scheme_row(self, row: dict) -> Scheme:
        """
        Parse a CSV row into a Scheme object.
        
        Args:
            row: Dictionary representing a CSV row
            
        Returns:
            Scheme object
        """
        # Parse list fields (benefits, eligibility, etc.)
        benefits = self._parse_list_field(row.get('benefits', ''))
        eligibility = self._parse_list_field(row.get('eligibility', ''))
        application_process = self._parse_list_field(row.get('application_process', ''))
        documents_required = self._parse_list_field(row.get('documents_required', ''))
        
        # Parse FAQs (JSON format)
        faqs = self._parse_faqs(row.get('faqs', ''))
        
        return Scheme(
            scheme_name=row.get('scheme_name', ''),
            state_name=row.get('state_name', ''),
            scheme_url=row.get('scheme_url', ''),
            details=row.get('details', ''),
            benefits=benefits,
            eligibility=eligibility,
            application_process=application_process,
            documents_required=documents_required,
            faqs=faqs
        )
    
    def _parse_list_field(self, field_value: str) -> List[str]:
        """
        Parse a list field from CSV (stored as JSON array string).
        
        Args:
            field_value: String representation of list
            
        Returns:
            List of strings
        """
        if not field_value or field_value.strip() == '':
            return []
        
        try:
            # Try parsing as JSON array
            parsed = json.loads(field_value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed]
            else:
                return [str(parsed).strip()]
        except json.JSONDecodeError:
            # If not valid JSON, split by common delimiters
            return [item.strip() for item in field_value.split('|') if item.strip()]
    
    def _parse_faqs(self, faq_value: str) -> List[dict]:
        """
        Parse FAQs from JSON string.
        
        Args:
            faq_value: JSON string of FAQ list
            
        Returns:
            List of FAQ dictionaries
        """
        if not faq_value or faq_value.strip() == '':
            return []
        
        try:
            faqs = json.loads(faq_value)
            if isinstance(faqs, list):
                return faqs
            else:
                return []
        except json.JSONDecodeError:
            return []
    
    def get_scheme_by_name(self, name: str) -> Scheme:
        """
        Get a specific scheme by name.
        
        Args:
            name: Scheme name to search for
            
        Returns:
            Scheme object if found, None otherwise
        """
        for scheme in self.schemes:
            if scheme.scheme_name.lower() == name.lower():
                return scheme
        return None
    
    def filter_by_state(self, state: str) -> List[Scheme]:
        """
        Filter schemes by state.
        
        Args:
            state: State name
            
        Returns:
            List of schemes for the specified state
        """
        return [s for s in self.schemes if s.state_name.lower() == state.lower()]
