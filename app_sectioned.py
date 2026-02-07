"""
Flask Application with Section-based Questionnaire
Questions are asked section by section with conditional flow
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.sectioned_questionnaire import SectionedQuestionnaire, SectionStatus

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'sectioned-questionnaire-demo-key-2024'  # Required for sessions
app.secret_key = 'sectioned_questionnaire_2026'


@app.route('/')
def home():
    """Home page"""
    # Create stats for the homepage
    questionnaire = SectionedQuestionnaire()
    stats = {
        "total_schemes": 0,  # You can update this when you integrate with actual scheme data
        "total_questions": len([q for section in questionnaire.sections for q in section.questions]),
        "sections": len(questionnaire.sections)
    }
    return render_template('index_new.html', stats=stats)


@app.route('/start-questionnaire')
def start_questionnaire():
    """Initialize a new questionnaire session"""
    # Create new questionnaire
    questionnaire = SectionedQuestionnaire()
    
    # Store simplified session data that can be serialized
    session_data = questionnaire.to_dict()
    
    # Ensure session data is JSON serializable
    session['questionnaire_data'] = session_data
    session['responses'] = {}
    session['current_section_id'] = questionnaire.current_section_id
    
    print(f"DEBUG: Session stored successfully")
    print(f"DEBUG: Session keys after storing: {list(session.keys())}")
    
    return redirect(url_for('questionnaire'))


@app.route('/find-schemes')
def find_schemes():
    """Redirect to start questionnaire (for compatibility with homepage links)"""
    return redirect(url_for('start_questionnaire'))


@app.route('/all-schemes')
def all_schemes():
    """Show all schemes (placeholder for now)"""
    return render_template('sectioned_results.html', 
                         responses={"message": "All schemes feature coming soon!"})


@app.route('/questionnaire')
def questionnaire():
    """Display current section of the questionnaire"""
    print(f"DEBUG: Questionnaire route called")
    print(f"DEBUG: Session keys: {list(session.keys())}")
    print(f"DEBUG: 'questionnaire_data' in session: {'questionnaire_data' in session}")
    
    if 'questionnaire_data' not in session:
        print("DEBUG: No questionnaire_data found, redirecting to start")
        return redirect(url_for('start_questionnaire'))
    
    # Reconstruct questionnaire from session
    q_data = session['questionnaire_data']
    
    print(f"DEBUG: Looking for current section: {q_data['current_section_id']}")
    print(f"DEBUG: Available sections: {[s['id'] for s in q_data['sections']]}")
    
    # Find current section
    current_section = None
    for section in q_data['sections']:
        if section['id'] == q_data['current_section_id']:
            current_section = section
            break
    
    if not current_section:
        print("DEBUG: No current section found, redirecting to results")
        return redirect(url_for('results'))
    
    print(f"DEBUG: Displaying section {current_section['id']} - {current_section['name']}")
    print(f"DEBUG: Current responses: {session.get('responses', {})}")
    
    return render_template('sectioned_questionnaire.html',
                         section=current_section,
                         progress=q_data['progress'],
                         responses=session.get('responses', {}))


@app.route('/submit-section', methods=['POST'])
def submit_section():
    """Process section submission and move to next"""
    if 'questionnaire_data' not in session:
        return jsonify({"error": "Session expired"}), 400
    
    # Recreate questionnaire
    questionnaire = SectionedQuestionnaire()
    
    # Restore previous responses
    if 'responses' in session:
        questionnaire.user_responses = session['responses']
    
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
    
    # Update session
    session['responses'] = questionnaire.user_responses
    
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
    
    # Update session data
    session['questionnaire_data'] = questionnaire.to_dict()
    
    if moved:
        return redirect(url_for('questionnaire'))
    else:
        # No more sections or condition not met
        return redirect(url_for('results'))


@app.route('/results')
def results():
    """Display final results based on responses"""
    if 'responses' not in session:
        return redirect(url_for('home'))
    
    responses = session['responses']
    
    # TODO: Match with schemes based on responses
    # For now, just display what was collected
    
    return render_template('sectioned_results.html',
                         responses=responses)


@app.route('/api/questionnaire/state', methods=['GET'])
def get_questionnaire_state():
    """API endpoint to get current questionnaire state"""
    if 'questionnaire_data' not in session:
        return jsonify({"error": "No active questionnaire"}), 404
    
    return jsonify(session['questionnaire_data'])


@app.route('/api/section/validate', methods=['POST'])
def validate_section():
    """API endpoint to validate section completion"""
    section_id = request.json.get('section_id')
    responses = request.json.get('responses', {})
    
    # Recreate questionnaire
    questionnaire = SectionedQuestionnaire()
    questionnaire.user_responses = responses
    
    section = questionnaire.get_section_by_id(section_id)
    if not section:
        return jsonify({"error": "Section not found"}), 404
    
    is_complete = questionnaire.is_section_complete(section)
    
    return jsonify({
        "is_complete": is_complete,
        "section_id": section_id
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001)
