"""
Demo: Section-based Conditional Questionnaire
This demonstrates how the questionnaire works with conditional sections
"""

from src.sectioned_questionnaire import SectionedQuestionnaire, SectionStatus
import json


def print_section(section):
    """Pretty print a section"""
    print(f"\n{'='*60}")
    print(f"📋 {section.name}")
    print(f"{'='*60}")
    print(f"Description: {section.description}")
    print(f"Status: {section.status.value}")
    print(f"Number of questions: {len(section.questions)}")
    print()


def print_question(question, index):
    """Pretty print a question"""
    required = " *" if question.required else ""
    print(f"{index}. {question.text}{required}")
    if question.type == "select":
        print(f"   Options: {', '.join(question.options)}")
    print(f"   Type: {question.type}")
    print()


def demo_basic_flow():
    """Demonstrate basic questionnaire flow"""
    print("\n" + "="*60)
    print("🎯 DEMO: Section-Based Questionnaire")
    print("="*60)
    
    # Create questionnaire
    q = SectionedQuestionnaire()
    
    print(f"\n✅ Initialized with {len(q.sections)} sections")
    print(f"📍 Current section: {q.current_section_id}")
    
    # Show progress
    progress = q.get_progress()
    print(f"\n📊 Progress:")
    print(f"   - Total sections: {progress['total_sections']}")
    print(f"   - Completed: {progress['completed_sections']}")
    print(f"   - Current: {progress['current_section']}")
    print(f"   - Progress: {progress['progress_percentage']}%")
    
    # Show current section
    current = q.get_current_section()
    if current:
        print_section(current)
        print("Questions:")
        for i, question in enumerate(current.questions, 1):
            print_question(question, i)
    
    # Simulate answering Section A
    print("\n" + "-"*60)
    print("🖊️  Answering Section A (Basic Information)...")
    print("-"*60)
    
    q.save_response("state", "Bihar")
    print("✓ State: Bihar")
    
    q.save_response("age", 25)
    print("✓ Age: 25")
    
    q.save_response("gender", "Male")
    print("✓ Gender: Male")
    
    q.save_response("category", "General")
    print("✓ Category: General")
    
    # Check if section is complete
    if q.is_section_complete(current):
        print("\n✅ Section A is complete!")
        
        # Try to move to next section
        if q.move_to_next_section():
            print("➡️  Moved to next section")
            
            # Show new current section
            current = q.get_current_section()
            if current:
                print_section(current)
                
                # Show updated progress
                progress = q.get_progress()
                print(f"📊 Updated Progress: {progress['progress_percentage']}%")
    
    # Simulate answering Section B
    print("\n" + "-"*60)
    print("🖊️  Answering Section B (Economic Status)...")
    print("-"*60)
    
    q.save_response("annual_income", 50000)
    print("✓ Annual Income: ₹50,000")
    
    q.save_response("is_bpl", True)
    print("✓ BPL Card: Yes")
    
    q.save_response("is_ultra_poor", False)
    print("✓ Ultra Poor: No")
    
    q.save_response("belong_to_rural_area", True)
    print("✓ Rural Area: Yes")
    
    # Move to next section
    if q.is_section_complete(current):
        print("\n✅ Section B is complete!")
        if q.move_to_next_section():
            print("➡️  Moved to Section C")
            
    # Continue with Section C
    current = q.get_current_section()
    if current:
        print_section(current)
        
        # Answer occupation questions
        print("🖊️  Answering occupation questions...")
        q.save_response("occupation", "Farmer")
        q.save_response("is_farmer", True)
        q.save_response("is_construction_worker", False)
        q.save_response("is_student", False)
        
        if q.is_section_complete(current):
            print("\n✅ Section C is complete!")
            
            # Check what sections are available next
            next_section = q.get_next_section()
            if next_section:
                print(f"\n🔜 Next available section: {next_section.name}")
                print(f"   Reason: User is a farmer, so farmer-specific questions will be shown")
    
    # Show final state
    print("\n" + "="*60)
    print("📊 FINAL STATE")
    print("="*60)
    
    final_progress = q.get_progress()
    print(f"Completed sections: {final_progress['completed_sections']}/{final_progress['total_sections']}")
    print(f"Progress: {final_progress['progress_percentage']}%")
    print(f"\nTotal responses collected: {len(q.user_responses)}")
    
    print("\n📝 All Responses:")
    for key, value in q.user_responses.items():
        print(f"   {key}: {value}")
    
    # Export to JSON
    print("\n💾 Exporting questionnaire state to JSON...")
    state = q.to_dict()
    
    with open('questionnaire_demo_state.json', 'w') as f:
        json.dump(state, f, indent=2)
    print("✅ Saved to: questionnaire_demo_state.json")


def demo_conditional_logic():
    """Demonstrate conditional section unlocking"""
    print("\n" + "="*60)
    print("🎯 DEMO: Conditional Section Logic")
    print("="*60)
    
    q = SectionedQuestionnaire()
    
    print("\n📋 Testing different scenarios:")
    
    # Scenario 1: User from other state
    print("\n1️⃣  Scenario: User from outside Bihar")
    print("   State: Other")
    q.save_response("state", "Other")
    
    section_b = q.get_section_by_id("section_b")
    can_access = q.check_section_condition(section_b)
    print(f"   Can access Economic Status section? {can_access}")
    print(f"   Reason: Section B requires state == Bihar")
    
    # Scenario 2: Young user
    print("\n2️⃣  Scenario: User under 18")
    print("   Age: 15")
    q.user_responses["age"] = 15
    
    section_c = q.get_section_by_id("section_c")
    can_access = q.check_section_condition(section_c)
    print(f"   Can access Occupation section? {can_access}")
    print(f"   Reason: Section C requires age >= 18")
    
    # Scenario 3: Not a farmer
    print("\n3️⃣  Scenario: User is not a farmer")
    print("   is_farmer: No")
    q.user_responses["is_farmer"] = False
    
    section_e = q.get_section_by_id("section_e")
    can_access = q.check_section_condition(section_e)
    print(f"   Can access Farmer Details section? {can_access}")
    print(f"   Reason: Section E requires is_farmer == True")
    
    # Scenario 4: Valid Bihar farmer
    print("\n4️⃣  Scenario: Valid Bihar farmer, age 25")
    q.user_responses = {
        "state": "Bihar",
        "age": 25,
        "is_farmer": True
    }
    
    section_b = q.get_section_by_id("section_b")
    section_c = q.get_section_by_id("section_c")
    section_e = q.get_section_by_id("section_e")
    
    print(f"   Can access Economic Status? {q.check_section_condition(section_b)}")
    print(f"   Can access Occupation? {q.check_section_condition(section_c)}")
    print(f"   Can access Farmer Details? {q.check_section_condition(section_e)}")


if __name__ == "__main__":
    print("\n🚀 Starting Sectioned Questionnaire Demo\n")
    
    # Run demos
    demo_basic_flow()
    print("\n" + "="*60 + "\n")
    demo_conditional_logic()
    
    print("\n\n✨ Demo completed! Check questionnaire_demo_state.json for exported state.\n")
