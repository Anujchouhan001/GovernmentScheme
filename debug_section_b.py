#!/usr/bin/env python3
"""
Debug script to test Section B to Section C transition
"""

import sys
sys.path.append('src')

from sectioned_questionnaire import SectionedQuestionnaire

def test_section_transition():
    questionnaire = SectionedQuestionnaire()
    
    print("=== Testing Section B to C Transition ===")
    
    # Simulate responses that should allow progression to Section C
    print("\n1. Starting with Section A responses:")
    questionnaire.save_response("state", "Bihar")
    questionnaire.save_response("age", 25)  # >= 18 should allow Section C
    questionnaire.save_response("gender", "Male")
    questionnaire.save_response("category", "General")
    
    print(f"Current responses: {questionnaire.user_responses}")
    print(f"Current section: {questionnaire.current_section_id}")
    
    # Complete Section A
    current = questionnaire.get_current_section()
    print(f"\n2. Completing Section A:")
    print(f"Section A complete: {questionnaire.is_section_complete(current)}")
    
    # Move to Section B
    moved = questionnaire.move_to_next_section()
    print(f"Moved to Section B: {moved}")
    print(f"Current section: {questionnaire.current_section_id}")
    
    # Complete Section B
    print("\n3. Adding Section B responses:")
    questionnaire.save_response("annual_income", 50000)
    questionnaire.save_response("is_bpl", False)
    questionnaire.save_response("is_ultra_poor", False)
    questionnaire.save_response("belong_to_rural_area", True)
    
    current = questionnaire.get_current_section()
    print(f"Section B complete: {questionnaire.is_section_complete(current)}")
    
    # Try to move to Section C
    print("\n4. Attempting to move to Section C:")
    next_section = questionnaire.get_next_section()
    print(f"Next section: {next_section.id if next_section else None}")
    
    if next_section:
        print(f"Next section conditions: {next_section.conditions}")
        condition_met = questionnaire.check_section_condition(next_section)
        print(f"Condition met: {condition_met}")
        
        # Check age condition specifically
        age_condition = {"field": "age", "operator": ">=", "value": 18}
        age_result = questionnaire._evaluate_condition(age_condition)
        print(f"Age condition (age >= 18): {age_result}")
        print(f"User age: {questionnaire.user_responses.get('age')}")
    
    moved_to_c = questionnaire.move_to_next_section()
    print(f"Successfully moved to Section C: {moved_to_c}")
    print(f"Final current section: {questionnaire.current_section_id}")

if __name__ == "__main__":
    test_section_transition()