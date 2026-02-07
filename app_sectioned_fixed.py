"""
Fixed Flask Application with Section-based Questionnaire
Simplified session handling to avoid serialization issues
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.sectioned_questionnaire import SectionedQuestionnaire, SectionStatus

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'sectioned-questionnaire-demo-key-2024'  # Required for sessions


@app.route('/')
def home():
    """Homepage with stats and navigation"""
    # Create stats for template
    stats = {
        'total_schemes': 0,  # Placeholder
        'total_questions': 38,  # Count from questionnaire
        'sections': 10  # Number of sections
    }
    
    return render_template('index_new.html', stats=stats)


@app.route('/start-questionnaire')
def start_questionnaire():
    """Initialize a new questionnaire session"""
    # Clear any existing session data
    session.clear()
    
    # Create new questionnaire
    questionnaire = SectionedQuestionnaire()
    
    # Store only essential data in session (JSON serializable)
    session['current_section_id'] = 'section_a'
    session['responses'] = {}
    session['section_status'] = {'section_a': 'in_progress'}
    
    print(f"DEBUG: Session initialized with section_a")
    
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
    
    if 'current_section_id' not in session:
        print("DEBUG: No session data found, redirecting to start")
        return redirect(url_for('start_questionnaire'))
    
    current_section_id = session['current_section_id']
    print(f"DEBUG: Current section ID: {current_section_id}")
    
    # Create fresh questionnaire and restore responses
    questionnaire = SectionedQuestionnaire()
    if session.get('responses'):
        questionnaire.user_responses = session['responses']
        # Update section status based on progression
        questionnaire.current_section_id = current_section_id
    
    current_section = questionnaire.get_section_by_id(current_section_id)
    
    if not current_section:
        print("DEBUG: No current section found, redirecting to results")
        return redirect(url_for('results'))
    
    print(f"DEBUG: Displaying section {current_section.id} - {current_section.name}")
    
    # Create progress info
    sections = ['section_a', 'section_b', 'section_c', 'section_d', 'section_e', 
               'section_f', 'section_g', 'section_h', 'section_i', 'section_j']
    current_index = sections.index(current_section_id) if current_section_id in sections else 0
    progress = {
        'total_sections': len(sections),
        'completed_sections': current_index,
        'current_section': current_section.name,
        'progress_percentage': int((current_index / len(sections)) * 100)
    }
    
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
    
    return render_template('sectioned_questionnaire.html',
                         section=section_dict,
                         progress=progress,
                         responses=session.get('responses', {}))


@app.route('/submit-section', methods=['POST'])
def submit_section():
    """Process section submission and move to next"""
    print(f"DEBUG: Submit section called")
    
    if 'current_section_id' not in session:
        return redirect(url_for('start_questionnaire'))
    
    # Create fresh questionnaire and restore state
    questionnaire = SectionedQuestionnaire()
    questionnaire.user_responses = session.get('responses', {})
    questionnaire.current_section_id = session['current_section_id']
    
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
    
    # Update session with responses
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
    
    if moved:
        # Update session with new current section
        session['current_section_id'] = questionnaire.current_section_id
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


if __name__ == '__main__':
    app.run(debug=True, port=5001)