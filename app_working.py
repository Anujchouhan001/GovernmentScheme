"""
Working Flask Application - No Complex Session Objects
Simple approach that works reliably in all environments
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.sectioned_questionnaire import SectionedQuestionnaire

app = Flask(__name__, template_folder='templates', static_folder='static')

# Global storage for active questionnaires (for demo purposes)
# In production, you'd use a proper database
active_questionnaires = {}

def get_questionnaire_id():
    """Simple way to identify questionnaires without sessions"""
    import time
    return str(int(time.time() * 1000))[-8:]  # Last 8 digits of timestamp


def load_schemes_data():
    """Load schemes eligibility data from JSON file"""
    try:
        with open('data/schemes_eligibility.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("WARNING: schemes_eligibility.json not found")
        return []


def map_questionnaire_to_profile(responses):
    """Map questionnaire responses to scheme matching profile"""
    profile = {}
    
    # Map basic demographic info
    profile['state_bihar'] = responses.get('state') == 'Bihar'
    profile['Age'] = responses.get('age', 0)
    profile['gender'] = responses.get('gender', '').lower()
    profile['category'] = responses.get('category', '')
    
    # Map economic info
    profile['annual_income'] = responses.get('annual_income', 0)
    profile['is_bpl'] = responses.get('is_bpl', False)
    profile['belong_to_rural_area'] = responses.get('belong_to_rural_area', False)
    
    # Map occupation info
    profile['occupation_farmer'] = responses.get('is_farmer', False)
    profile['occupation_construction'] = responses.get('is_construction_worker', False)
    profile['occupation_student'] = responses.get('is_student', False)
    
    # Map land info
    profile['land_owned_acres'] = responses.get('land_owned_acres', 0)
    
    # Map family info
    profile['marital_status'] = responses.get('marital_status', '')
    profile['num_children'] = responses.get('num_children', 0)
    profile['num_girl_children'] = responses.get('num_girl_children', 0)
    
    # Map identity info
    profile['has_aadhaar'] = responses.get('has_aadhaar', False)
    profile['bank_account_linked_aadhaar'] = responses.get('bank_account_linked_aadhaar', False)
    
    # Map health info
    profile['has_disability'] = responses.get('has_disability', False)
    profile['disability_percentage'] = responses.get('disability_percentage', 0)
    
    return profile


def calculate_scheme_match(scheme, profile):
    """Calculate how well a scheme matches the user profile"""
    total_criteria = len(scheme.get('eligibility_criteria', []))
    if total_criteria == 0:
        return 0, []
    
    matched_criteria = 0
    match_reasons = []
    
    for criteria in scheme['eligibility_criteria']:
        data_field = criteria.get('data_field', '').lower()
        eligibility_text = criteria.get('eligibility_text', '')
        
        # Enhanced matching logic
        matched = False
        
        # State matching
        if 'state_bihar' in data_field and profile.get('state_bihar'):
            matched = True
        
        # Age matching with range detection
        elif 'age' in data_field:
            age = profile.get('Age', 0)
            if 'between' in eligibility_text.lower():
                # Try to extract age range
                import re
                age_match = re.findall(r'\d+', eligibility_text)
                if len(age_match) >= 2:
                    min_age, max_age = int(age_match[0]), int(age_match[1])
                    if min_age <= age <= max_age:
                        matched = True
                elif '18' in eligibility_text and age >= 18:
                    matched = True
            elif age > 0:  # Any age requirement
                matched = True
        
        # Occupation matching
        elif 'farmer' in data_field and profile.get('occupation_farmer'):
            matched = True
        elif 'construction' in data_field and profile.get('occupation_construction'):
            matched = True
        elif 'student' in data_field and profile.get('occupation_student'):
            matched = True
        
        # Occupation specific matching
        elif 'farmer' in data_field.lower() or 'agriculture' in data_field.lower():
            if profile.get('occupation_farmer'):
                matched = True
        elif 'construction' in data_field.lower() or 'worker' in data_field.lower():
            if profile.get('occupation_construction'):
                matched = True
        elif 'student' in data_field.lower() or 'education' in data_field.lower():
            if profile.get('occupation_student'):
                matched = True
        
        # Economic status matching
        elif 'bpl' in data_field and profile.get('is_bpl'):
            matched = True
        elif 'rural' in data_field and profile.get('belong_to_rural_area'):
            matched = True
        elif 'income' in data_field:
            income = profile.get('annual_income', 0)
            if income > 0:
                matched = True
        
        # Identity document matching
        elif 'aadhaar' in data_field and profile.get('has_aadhaar'):
            matched = True
        elif 'bank' in data_field and profile.get('bank_account_linked_aadhaar'):
            matched = True
        
        # Land ownership matching
        elif 'land' in data_field:
            land_acres = profile.get('land_owned_acres', 0)
            if 'between' in eligibility_text.lower():
                # Extract land range using string parsing instead of regex
                # Text like "Land area between 0.25 acres and 5 acres"
                text_lower = eligibility_text.lower()
                try:
                    # Find numbers in the text
                    numbers = []
                    words = text_lower.split()
                    for word in words:
                        # Clean word and try to convert to float
                        clean_word = word.strip(',.()[]{}')
                        try:
                            num = float(clean_word)
                            numbers.append(num)
                        except ValueError:
                            continue
                    
                    if len(numbers) >= 2:
                        min_land, max_land = numbers[0], numbers[1]
                        if min_land <= land_acres <= max_land:
                            matched = True
                except:
                    # Fallback - if parsing fails, just check if user has land
                    if land_acres > 0:
                        matched = True
            elif land_acres > 0:
                matched = True
        
        # Category matching
        elif 'category' in data_field.lower() or 'caste' in data_field.lower():
            user_category = profile.get('category', '').lower()
            if 'obc' in data_field and 'obc' in user_category:
                matched = True
            elif 'sc' in data_field and 'sc' in user_category:
                matched = True
            elif 'st' in data_field and 'st' in user_category:
                matched = True
            elif 'minority' in data_field and 'minority' in user_category:
                matched = True
        
        # Gender matching
        elif 'gender' in data_field or 'woman' in data_field or 'female' in data_field:
            if profile.get('gender', '').lower() == 'female':
                matched = True
        
        # Disability matching
        elif 'disability' in data_field and profile.get('has_disability'):
            matched = True
        
        # Family/children matching
        elif 'children' in data_field or 'girl' in data_field:
            if profile.get('num_children', 0) > 0 or profile.get('num_girl_children', 0) > 0:
                matched = True
        
        # Marital status matching
        elif 'married' in data_field or 'marital' in data_field:
            marital_status = profile.get('marital_status', '').lower()
            if 'married' in marital_status:
                matched = True
        
        if matched:
            matched_criteria += 1
            match_reasons.append(eligibility_text)
    
    # Calculate match percentage
    match_score = (matched_criteria / total_criteria) * 100
    return match_score, match_reasons


def find_matching_schemes(responses, min_score=50):
    """Find schemes matching user responses - show schemes with 50% or higher match"""
    schemes_data = load_schemes_data()
    profile = map_questionnaire_to_profile(responses)
    
    matching_schemes = []
    
    for scheme in schemes_data:
        score, reasons = calculate_scheme_match(scheme, profile)
        
        if score >= min_score:
            matching_schemes.append({
                'name': scheme['name'],
                'score': score,
                'reasons': reasons,
                'eligibility_criteria': scheme.get('eligibility_criteria', [])
            })
    
    # Sort by match score (highest first)
    matching_schemes.sort(key=lambda x: x['score'], reverse=True)
    
    return matching_schemes


@app.route('/')
def home():
    """Homepage with stats and navigation"""
    stats = {
        'total_schemes': 0,
        'total_questions': 38,
        'sections': 10
    }
    return render_template('index_new.html', stats=stats)


@app.route('/start-questionnaire')
def start_questionnaire():
    """Initialize a new questionnaire session"""
    # Create new questionnaire
    questionnaire = SectionedQuestionnaire()
    
    # Generate simple ID and store questionnaire
    q_id = get_questionnaire_id()
    active_questionnaires[q_id] = questionnaire
    
    print(f"DEBUG: Created questionnaire {q_id} with section {questionnaire.current_section_id}")
    
    return redirect(f'/questionnaire/{q_id}')


@app.route('/questionnaire/<q_id>')
def questionnaire(q_id):
    """Display current section of the questionnaire"""
    if q_id not in active_questionnaires:
        print(f"DEBUG: Questionnaire {q_id} not found")
        return redirect(url_for('start_questionnaire'))
    
    questionnaire = active_questionnaires[q_id]
    current_section = questionnaire.get_current_section()
    
    if not current_section:
        print("DEBUG: No current section found, redirecting to results")
        return redirect(f'/results/{q_id}')
    
    print(f"DEBUG: Displaying section {current_section.id} for questionnaire {q_id}")
    
    # Convert section to dict format for template
    section_dict = {
        'id': current_section.id,
        'name': current_section.name,
        'description': current_section.description,
        'questions': [
            {
                'id': q.id,
                'text': q.text,
                'type': q.type,
                'required': q.required,
                'options': q.options,
                'condition': q.condition
            }
            for q in current_section.questions
        ]
    }
    
    progress = questionnaire.get_progress()
    
    return render_template('sectioned_questionnaire.html',
                         section=section_dict,
                         progress=progress,
                         responses=questionnaire.user_responses,
                         questionnaire_id=q_id)


@app.route('/submit-section/<q_id>', methods=['POST'])
def submit_section(q_id):
    """Process section submission and move to next"""
    if q_id not in active_questionnaires:
        return redirect(url_for('start_questionnaire'))
    
    questionnaire = active_questionnaires[q_id]
    
    # Get form data
    section_id = request.form.get('section_id')
    
    # Save all responses from this section
    current_section = questionnaire.get_section_by_id(section_id)
    if current_section:
        for question in current_section.questions:
            answer = request.form.get(question.id)
            if answer is not None and answer != '':
                # Convert based on type
                if question.type == 'number':
                    try:
                        answer = float(answer)
                        if answer == int(answer):
                            answer = int(answer)
                    except ValueError:
                        pass
                elif question.type == 'yes_no':
                    answer = answer.lower() == 'yes' or answer.lower() == 'true'
                
                questionnaire.save_response(question.id, answer)
                
                # Auto-detection logic for occupation
                if question.id == 'occupation':
                    # Auto-set related occupation flags based on primary occupation
                    if answer == 'Farmer':
                        questionnaire.save_response('is_farmer', True)
                        questionnaire.save_response('is_construction_worker', False)
                        questionnaire.save_response('is_student', False)
                    elif answer == 'Construction Worker':
                        questionnaire.save_response('is_construction_worker', True)
                        questionnaire.save_response('is_farmer', False)
                        questionnaire.save_response('is_student', False)
                    elif answer == 'Student':
                        questionnaire.save_response('is_student', True)
                        questionnaire.save_response('is_farmer', False)
                        questionnaire.save_response('is_construction_worker', False)
                
                # Auto-detection logic for occupation
                if question.id == 'occupation':
                    # Auto-set related occupation flags
                    if answer == 'Farmer':
                        questionnaire.save_response('is_farmer', True)
                    elif answer == 'Construction Worker':
                        questionnaire.save_response('is_construction_worker', True)
                    elif answer == 'Student':
                        questionnaire.save_response('is_student', True)
    
    # Try to move to next section
    moved = questionnaire.move_to_next_section()
    
    # Debug information
    print(f"DEBUG: Current responses: {questionnaire.user_responses}")
    print(f"DEBUG: Moved to next section: {moved}")
    if not moved:
        current_section = questionnaire.get_current_section()
        next_section = questionnaire.get_next_section()
        print(f"DEBUG: Current section: {current_section.id if current_section else None}")
        print(f"DEBUG: Next section: {next_section.id if next_section else None}")
        if next_section:
            print(f"DEBUG: Next section conditions: {next_section.conditions}")
            print(f"DEBUG: Condition check result: {questionnaire.check_section_condition(next_section)}")
    
    if moved:
        return redirect(f'/questionnaire/{q_id}')
    else:
        # No more sections or condition not met
        return redirect(f'/results/{q_id}')


@app.route('/results/<q_id>')
def results(q_id):
    """Display final results based on responses"""
    if q_id not in active_questionnaires:
        return redirect(url_for('home'))
    
    questionnaire = active_questionnaires[q_id]
    responses = questionnaire.user_responses
    
    # Find matching schemes with lower threshold for better results
    matching_schemes = find_matching_schemes(responses, min_score=30)
    
    print(f"DEBUG: Found {len(matching_schemes)} matching schemes")
    if matching_schemes:
        print(f"DEBUG: Top scheme score: {matching_schemes[0]['score']}%")
    
    return render_template('sectioned_results.html', 
                         responses=responses,
                         matching_schemes=matching_schemes,
                         questionnaire_id=q_id)


@app.route('/debug-schemes/<q_id>')
def debug_schemes(q_id):
    '''Debug endpoint to test scheme matching'''
    if q_id not in active_questionnaires:
        return f"Questionnaire {q_id} not found"
    
    questionnaire = active_questionnaires[q_id]
    responses = questionnaire.user_responses
    
    # Debug info
    debug_info = """
    <h2>Debug Scheme Matching</h2>
    <h3>User Responses:</h3>
    <pre>{}</pre>
    
    <h3>Mapped Profile:</h3>
    """.format(json.dumps(responses, indent=2))
    
    profile = map_questionnaire_to_profile(responses)
    debug_info += "<pre>{}</pre>".format(json.dumps(profile, indent=2))
    
    # Test with first few schemes
    schemes_data = load_schemes_data()
    debug_info += "<h3>Testing First 3 Schemes:</h3>"
    
    for i, scheme in enumerate(schemes_data[:3]):
        score, reasons = calculate_scheme_match(scheme, profile)
        debug_info += """
        <h4>{}. {}</h4>
        <p>Score: {}%</p>
        <p>Matched criteria:</p>
        <ul>
        """.format(i+1, scheme['name'], score)
        for reason in reasons:
            debug_info += "<li>{}</li>".format(reason)
        debug_info += "</ul>"
    
    return debug_info


@app.route('/find-schemes/<q_id>')
def find_schemes_for_questionnaire(q_id):
    """Find and display schemes for completed questionnaire"""
    if q_id not in active_questionnaires:
        return redirect(url_for('home'))
    
    questionnaire = active_questionnaires[q_id]
    responses = questionnaire.user_responses
    
    # Find matching schemes - only 100% matches
    matching_schemes = find_matching_schemes(responses, min_score=100)
    
    return render_template('scheme_results.html',
                         matching_schemes=matching_schemes,
                         responses=responses,
                         questionnaire_id=q_id)


@app.route('/find-schemes')
def find_schemes():
    """Redirect to start questionnaire"""
    return redirect(url_for('start_questionnaire'))


@app.route('/all-schemes')
def all_schemes():
    """Show all schemes (placeholder)"""
    return render_template('sectioned_results.html', 
                         responses={"message": "All schemes feature coming soon!"})


if __name__ == '__main__':
    app.run(debug=True, port=5001)

# For Vercel deployment
app = app