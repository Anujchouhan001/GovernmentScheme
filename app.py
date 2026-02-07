"""
Updated Scheme Finder - Flask Web Application
Uses the new questionnaire system based on Excel data
"""

from flask import Flask, render_template, request, jsonify, session
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.new_questionnaire import SchemeQuestionnaire, UserResponse

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'scheme_finder_secret_key_2026'

# Initialize questionnaire system
questionnaire = SchemeQuestionnaire()

# Section icons for UI
SECTION_ICONS = {
    "Basic Information": "user",
    "Category & Economic Status": "money-bill-wave",
    "Identity Documents": "id-card",
    "Marital Status": "heart",
    "Family Information": "users",
    "Land & Property": "home",
    "Occupation": "briefcase",
    "Farmer Details": "tractor",
    "Construction Worker Details": "hard-hat",
    "Business Details": "store",
    "Education Details": "graduation-cap",
    "Competitive Exams": "file-alt",
    "Hostel Details": "building",
    "Employment": "user-tie",
    "Disability": "wheelchair",
    "Medical Conditions": "heartbeat",
    "Journalist Details": "newspaper",
    "Fisherman Details": "fish",
    "Unorganized Sector": "tools",
    "Women Specific": "female",
    "Death Benefit": "cross",
    "Pension": "coins",
    "Training": "certificate",
    "Previous Benefits": "history",
    "Other": "ellipsis-h",
    "Location": "map-marker-alt"
}


@app.route('/')
def home():
    """Home page with introduction."""
    stats = {
        "total_schemes": len(questionnaire.schemes),
        "total_questions": len(questionnaire.get_all_questions()),
        "sections": len(questionnaire.get_sections())
    }
    return render_template('index_new.html', stats=stats)


@app.route('/find-schemes')
def find_schemes():
    """New questionnaire page with all questions from Excel."""
    questions = questionnaire.get_all_questions()
    sections = questionnaire.get_sections()
    
    return render_template('questionnaire_new.html', 
                         questions=questions,
                         sections=sections,
                         section_icons=SECTION_ICONS)


@app.route('/results', methods=['POST'])
def results():
    """Process form and show results with exact matching."""
    # Create new questionnaire instance for this request
    q = SchemeQuestionnaire()
    
    # Process all form data
    for key, value in request.form.items():
        if value:
            # Convert values appropriately
            if value == 'yes':
                q.set_response(key, True)
            elif value == 'no':
                q.set_response(key, False)
            else:
                # Try to convert to number
                try:
                    num_val = float(value)
                    q.set_response(key, int(num_val) if num_val == int(num_val) else num_val)
                except ValueError:
                    q.set_response(key, value)
    
    # Find only 100% eligible schemes
    eligible_schemes = q.find_eligible_schemes(only_fully_eligible=True)
    
    # Prepare user summary for display
    user_summary = {
        "state": "Bihar" if q.user_response.state_bihar else "Other",
        "age": q.user_response.age,
        "gender": q.user_response.gender,
        "category": q.user_response.category,
        "occupation": q.user_response.occupation,
        "annual_income": q.user_response.annual_income,
        "is_bpl": q.user_response.is_bpl
    }
    
    return render_template('results_new.html', 
                         schemes=eligible_schemes, 
                         fully_eligible=eligible_schemes,
                         partial_matches=[],
                         user=user_summary,
                         total_found=len(eligible_schemes),
                         total_schemes=len(q.schemes))


@app.route('/scheme/<scheme_name>')
def scheme_detail(scheme_name):
    """Show detailed scheme information."""
    for scheme in questionnaire.schemes:
        if scheme['name'] == scheme_name:
            return render_template('scheme_detail_new.html', scheme=scheme)
    return "Scheme not found", 404


@app.route('/all-schemes')
def all_schemes():
    """Show all available schemes."""
    return render_template('all_schemes_new.html', schemes=questionnaire.schemes)


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@app.route('/api/schemes')
def api_schemes():
    """API endpoint to get all schemes as JSON."""
    scheme_list = []
    for scheme in questionnaire.schemes:
        scheme_list.append({
            'name': scheme['name'],
            'criteria_count': len(scheme.get('eligibility_criteria', []))
        })
    return jsonify(scheme_list)


@app.route('/api/questions')
def api_questions():
    """API endpoint to get all questions as JSON."""
    return jsonify(questionnaire.get_all_questions())


@app.route('/api/check-eligibility', methods=['POST'])
def api_check_eligibility():
    """API endpoint to check eligibility based on JSON input."""
    data = request.json
    
    q = SchemeQuestionnaire()
    for key, value in data.items():
        q.set_response(key, value)
    
    eligible_schemes = q.find_eligible_schemes()
    
    return jsonify({
        "total_schemes": len(q.schemes),
        "eligible_count": len(eligible_schemes),
        "eligible_schemes": eligible_schemes
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  BIHAR SCHEME FINDER WEB APPLICATION")
    print("="*60)
    print(f"  Loaded {len(questionnaire.schemes)} government schemes")
    print(f"  Total questions: {len(questionnaire.get_all_questions())}")
    print(f"  Sections: {len(questionnaire.get_sections())}")
    print("  Open browser: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)
