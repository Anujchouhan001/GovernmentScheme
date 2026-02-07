"""
Utility functions for Scheme Finder application.
"""

import re
from typing import List, Dict, Any
import json


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra quotes
    text = text.replace('""', '').strip('"')
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def extract_number(text: str) -> float:
    """
    Extract the first number found in text.
    
    Args:
        text: Input text
        
    Returns:
        First number found, or 0 if none found
    """
    match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)', text)
    if match:
        return float(match.group(1).replace(',', ''))
    return 0.0


def format_currency(amount: float) -> str:
    """
    Format amount as Indian currency.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
    """
    if amount >= 10000000:  # 1 crore or more
        return f"₹{amount/10000000:.2f} Crore"
    elif amount >= 100000:  # 1 lakh or more
        return f"₹{amount/100000:.2f} Lakh"
    else:
        return f"₹{amount:,.0f}"


def parse_age_range(text: str) -> tuple:
    """
    Extract age range from text.
    
    Args:
        text: Text containing age information
        
    Returns:
        Tuple of (min_age, max_age) or (None, None)
    """
    pattern = r'(\d+)\s*(?:and|to|-)\s*(\d+)\s*years?'
    match = re.search(pattern, text.lower())
    
    if match:
        return (int(match.group(1)), int(match.group(2)))
    
    return (None, None)


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    text = clean_text(text)
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def validate_user_input(
    value: Any, 
    input_type: str, 
    min_val: Any = None, 
    max_val: Any = None
) -> bool:
    """
    Validate user input.
    
    Args:
        value: Value to validate
        input_type: Type of input (number, text, choice)
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if input_type == 'number':
            val = float(value)
            if min_val is not None and val < min_val:
                return False
            if max_val is not None and val > max_val:
                return False
            return True
        
        elif input_type == 'text':
            return bool(str(value).strip())
        
        elif input_type == 'choice':
            return value in (min_val or [])
        
    except (ValueError, TypeError):
        return False
    
    return True


def load_json_file(filepath: str) -> Dict:
    """
    Load JSON file safely.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Dictionary from JSON, or empty dict if error
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file {filepath}: {e}")
        return {}


def save_json_file(data: Dict, filepath: str):
    """
    Save dictionary to JSON file.
    
    Args:
        data: Dictionary to save
        filepath: Output file path
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving JSON file {filepath}: {e}")


def get_keywords_from_text(text: str, keyword_list: List[str]) -> List[str]:
    """
    Extract keywords from text.
    
    Args:
        text: Input text
        keyword_list: List of keywords to search for
        
    Returns:
        List of found keywords
    """
    text_lower = text.lower()
    found = []
    
    for keyword in keyword_list:
        if keyword.lower() in text_lower:
            found.append(keyword)
    
    return found


def calculate_percentage_match(profile_dict: Dict, scheme_dict: Dict) -> float:
    """
    Calculate percentage match between profile and scheme.
    
    Args:
        profile_dict: User profile as dictionary
        scheme_dict: Scheme requirements as dictionary
        
    Returns:
        Match percentage (0-100)
    """
    matches = 0
    total = 0
    
    for key, value in scheme_dict.items():
        if value is None:  # No requirement
            continue
        
        total += 1
        
        if key in profile_dict:
            if profile_dict[key] == value:
                matches += 1
    
    if total == 0:
        return 100.0  # No requirements means 100% match
    
    return (matches / total) * 100
