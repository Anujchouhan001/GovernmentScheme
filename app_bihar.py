"""
Flask Web Application for Bihar Scheme Finder
Implements orange/black question logic with 100% eligibility matching
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
from datetime import datetime
import os
import sys
import uuid

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.bihar_questionnaire import BiharQuestionnaire, Question, BiharScheme

app = Flask(__name__)
app.secret_key = 'bihar_scheme_finder_2024'

# ---- Server-side questionnaire storage (avoids cookie 4KB limit) ----
questionnaire_store = {}

def get_questionnaire() -> BiharQuestionnaire:
    """Get or create the questionnaire for the current session."""
    sid = session.get('sid')
    if sid and sid in questionnaire_store:
        return questionnaire_store[sid]
    # New session
    sid = str(uuid.uuid4())
    session['sid'] = sid
    q = BiharQuestionnaire()
    questionnaire_store[sid] = q
    return q


@app.route('/')
def index():
    """Home page with option to start Bihar questionnaire"""
    return render_template('bihar_index.html')


@app.route('/questionnaire')
def questionnaire():
    """Start or continue Bihar questionnaire"""
    get_questionnaire()  # ensure session is initialized
    return render_template('bihar_questionnaire.html')


@app.route('/api/get_question', methods=['GET'])
def get_question():
    """Get the current question to display"""
    try:
        q = get_questionnaire()
        current_question = q.get_current_question()
        progress = q.get_progress()
        
        if current_question is None:
            return jsonify({
                'status': 'complete',
                'progress': progress
            })
        
        return jsonify({
            'status': 'active',
            'question': {
                'id': current_question.id,
                'text': current_question.text,
                'question_type': current_question.question_type,
                'input_type': current_question.input_type,
                'options': current_question.options,
                'required': current_question.required
            },
            'progress': progress
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 500


@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """Submit answer for current question"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        if not question_id or answer is None:
            return jsonify({
                'status': 'error',
                'message': 'Missing question_id or answer'
            }), 400
        
        q = get_questionnaire()
        
        # If user answers "No" to Bihar residency (Q2), reject immediately
        if question_id == 'q_2' and str(answer).strip() == 'No':
            return jsonify({
                'status': 'not_bihar',
                'message': 'This service is only for residents of Bihar. You must be a resident of Bihar to find eligible government schemes.'
            })
        
        success = q.submit_answer(question_id, answer)
        
        if success:
            if q.is_complete():
                return jsonify({
                    'status': 'complete',
                    'message': 'Questionnaire completed successfully'
                })
            else:
                return jsonify({
                    'status': 'success',
                    'message': 'Answer submitted successfully'
                })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to submit answer'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/results')
def results():
    """Show eligible schemes results"""
    try:
        q = get_questionnaire()
        eligible_schemes = q.get_eligible_schemes()
        
        return render_template('bihar_results.html', 
                             schemes=eligible_schemes,
                             total_schemes=len(eligible_schemes))
        
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/scheme/<scheme_name>')
def scheme_detail(scheme_name):
    """Show detailed information for a specific scheme"""
    try:
        q = get_questionnaire()
        
        scheme = None
        for s in q.schemes:
            if s.name == scheme_name:
                scheme = s
                break
        
        if not scheme:
            return render_template('error.html', error="Scheme not found")
        
        return render_template('bihar_scheme_detail.html', scheme=scheme)
        
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/api/reset_questionnaire', methods=['POST'])
def reset_questionnaire():
    """Reset the questionnaire to start over"""
    try:
        sid = session.get('sid')
        if sid and sid in questionnaire_store:
            del questionnaire_store[sid]
        session.pop('sid', None)
        return jsonify({
            'status': 'success',
            'message': 'Questionnaire reset successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 500


@app.route('/about')
def about():
    """About page with information about Bihar schemes"""
    return render_template('bihar_about.html')


@app.route('/api/schemes_stats', methods=['GET'])
def schemes_stats():
    """Get statistics about Bihar schemes"""
    try:
        q = get_questionnaire()
        
        total_schemes = len(q.schemes)
        scheme_categories = {}
        
        for scheme in q.schemes:
            name_lower = scheme.name.lower()
            if any(word in name_lower for word in ['pension', 'suraksha', 'kalyan']):
                category = 'Social Security'
            elif any(word in name_lower for word in ['krishi', 'fasal', 'farmer']):
                category = 'Agriculture' 
            elif any(word in name_lower for word in ['udyami', 'startup', 'business']):
                category = 'Business & Employment'
            elif any(word in name_lower for word in ['education', 'scholarship', 'chhatravas']):
                category = 'Education'
            elif any(word in name_lower for word in ['health', 'medical', 'aids']):
                category = 'Healthcare'
            else:
                category = 'Other'
            
            scheme_categories[category] = scheme_categories.get(category, 0) + 1
        
        return jsonify({
            'total_schemes': total_schemes,
            'categories': scheme_categories,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)