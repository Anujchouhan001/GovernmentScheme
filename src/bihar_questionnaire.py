"""
Bihar Questionnaire System with Orange/Black Question Logic
Orange questions are main questions - if answered "Yes", show related black (sub) questions
Only eligible schemes (100% match) are shown to users
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import pandas as pd


@dataclass
class Question:
    """Individual question with conditional logic"""
    id: str
    text: str
    question_type: str  # orange (main), black (sub)
    input_type: str  # yes_no, text, select, number
    options: List[str] = field(default_factory=list)
    column: str = ""  # Column name for data storage
    parent_question: Optional[str] = None  # For black questions
    condition_value: str = "Yes"  # Value that triggers sub-questions
    required: bool = True
    occupation_category: Optional[str] = None  # For Q13 occupation sub-questions
    is_category_header: bool = False  # Category headers (e.g., "Business", "Farmer") - skip during display


@dataclass 
class BiharScheme:
    """Bihar government scheme information"""
    name: str
    eligibility_criteria: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    benefits: List[str] = field(default_factory=list)
    application_process: List[str] = field(default_factory=list)
    required_documents: List[str] = field(default_factory=list)


class BiharQuestionnaire:
    """
    Bihar-specific questionnaire system with orange/black question logic
    """
    
    def __init__(self):
        self.questions: List[Question] = []
        self.schemes: List[BiharScheme] = []
        self.user_responses: Dict[str, Any] = {}
        self.current_question_index = 0
        self._load_questions()
        self._load_schemes()
    
    def _load_questions(self):
        """Load all questions from Bihar Excel data"""
        try:
            # Read the Excel file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, 'data', 'schemes_bihar.xlsx')
            df = pd.read_excel(file_path, sheet_name='final questions')
            
            all_questions = []
            last_main_question = None
            
            for idx, row in df.iterrows():
                if pd.notna(row['Unnamed: 1']):  # If there's a question text
                    question_num = row['Unnamed: 0'] if pd.notna(row['Unnamed: 0']) else None
                    question_text = str(row['Unnamed: 1']).strip()
                    options_text = str(row['Unnamed: 2']).strip() if pd.notna(row['Unnamed: 2']) else None
                    follow_up = str(row['Unnamed: 3']).strip() if pd.notna(row['Unnamed: 3']) else None
                    
                    # Determine if this is a main question (has number) or follow-up question (no number)
                    if question_num is not None and not pd.isna(question_num):
                        # Main question (orange)
                        question_type = "orange"
                        question_id = f"q_{int(question_num)}"
                        parent_question = None
                        condition_value = None
                        last_main_question = question_id
                    else:
                        # Follow-up question (black)
                        question_type = "black"
                        question_id = f"follow_up_{idx}"
                        parent_question = last_main_question
                        condition_value = "Yes"  # Most follow-ups appear when parent is "Yes"
                    
                    # Determine input type based on options
                    input_type = "text"
                    options = []
                    
                    if options_text and options_text != 'nan':
                        if "Yes/ No" in options_text:
                            input_type = "yes_no"
                            options = ["Yes", "No"]
                        elif "Specify" in options_text and ("actual in INR" in options_text or "in acres" in options_text or "Years" in options_text or "Numbers" in options_text or "percentage" in options_text or "Percentage" in options_text):
                            input_type = "number"
                        elif "/" in options_text and "Specify" not in options_text:
                            input_type = "select"
                            options = [opt.strip() for opt in options_text.split('/')]
                        else:
                            input_type = "text"
                    
                    question = Question(
                        id=question_id,
                        text=question_text,
                        question_type=question_type,
                        input_type=input_type,
                        options=options,
                        column=question_id,
                        parent_question=parent_question,
                        condition_value=condition_value,
                        required=True
                    )
                    
                    all_questions.append(question)
            
            self.questions = all_questions
            
            # Reorder: move marital status (Q17) before children (Q12)
            self._reorder_questions()
            
            # Tag Q13 occupation sub-questions with their category
            self._tag_occupation_questions()
            
            # Set Bihar district options for Q23 and block for Q22
            self._set_district_and_block_options()
            
            print(f"Loaded {len(self.questions)} questions from Excel file")
            
            # Count question types
            orange_count = sum(1 for q in self.questions if q.question_type == 'orange')
            black_count = sum(1 for q in self.questions if q.question_type == 'black')
            print(f"Orange (main) questions: {orange_count}")
            print(f"Black (follow-up) questions: {black_count}")
            
        except Exception as e:
            print(f"Error loading questions from Excel: {e}")
            # Fallback to basic questions if Excel loading fails
            self._load_basic_questions()
    
    def _load_basic_questions(self):
        """Fallback basic questions if Excel loading fails"""
        basic_questions = [
            Question(id="q_1", text="Are you a resident of Bihar?", question_type="main", input_type="yes_no", options=["Yes", "No"]),
            Question(id="q_2", text="What is your annual family income?", question_type="main", input_type="number"),
            Question(id="q_3", text="What is your age?", question_type="main", input_type="number"),
            Question(id="q_4", text="What is your gender?", question_type="main", input_type="select", options=["Male", "Female", "Other"]),
            Question(id="q_5", text="What is your social category?", question_type="main", input_type="select", options=["General", "SC", "ST", "OBC", "BC", "EBC", "Minority"]),
            Question(id="q_6", text="Are you registered on the Direct Benefit Transfer (DBT) portal?", question_type="main", input_type="yes_no", options=["Yes", "No"]),
            Question(id="q_7", text="Do you have a bank account?", question_type="main", input_type="yes_no", options=["Yes", "No"]),
            Question(id="q_8", text="Do you have a disability?", question_type="main", input_type="yes_no", options=["Yes", "No"]),
            Question(id="q_9", text="What is your current marital status?", question_type="main", input_type="select", options=["Unmarried", "Married", "Divorced", "Widowed", "Separated"]),
            Question(id="q_10", text="What is your occupation?", question_type="main", input_type="select", options=["Farmer", "Construction Worker", "Student", "Business", "Employment", "Journalist", "Unorganised Sector Worker", "Other"])
        ]
        self.questions = basic_questions
    
    def _tag_occupation_questions(self):
        """Tag Q13 sub-questions with their occupation category.
        Occupation headers (Business, Farmer, etc.) are marked as category headers
        and won't be displayed. Their following sub-questions are tagged with the
        category so only the relevant branch is shown based on user's occupation."""
        # Map of header text (lowercase, stripped) → occupation category name
        occupation_header_map = {
            'business': 'Business',
            'business startup': 'Business',  # sub-section of Business
            'construction worker': 'Construction Worker',
            'employment': 'Employment',
            'farmer': 'Farmer',
            'journalist or media representative': 'Journalist',
            'journalist': 'Journalist',
            'student': 'Student',
            'unorganised sector worker / craftsman': 'Unorganised Sector Worker',
            'unorganised sector worker': 'Unorganised Sector Worker',
            'other(specify)': 'Other',
            'other': 'Other',
        }
        
        occupation_options = []  # Ordered list of main occupation categories
        seen_categories = set()
        current_category = None
        
        for q in self.questions:
            if q.parent_question != "q_13":
                continue
            
            text_lower = q.text.strip().lower().rstrip('.')
            
            # Check if this is an occupation category header
            matched_category = None
            for header_key, category_name in occupation_header_map.items():
                if text_lower == header_key or text_lower.startswith(header_key):
                    matched_category = category_name
                    break
            
            if matched_category and (q.options is None or len(q.options) == 0 or q.input_type == 'text'):
                # This is a category header
                # Check if it has no real options (headers typically have null/empty options)
                is_header = (q.input_type == 'text' and (not q.options or q.options == []))
                if is_header:
                    q.is_category_header = True
                    current_category = matched_category
                    q.occupation_category = matched_category
                    if matched_category not in seen_categories:
                        occupation_options.append(matched_category)
                        seen_categories.add(matched_category)
                    continue
            
            # Regular sub-question: tag with current category
            q.occupation_category = current_category
        
        # Set Q13 as a select dropdown with occupation options
        for q in self.questions:
            if q.id == "q_13":
                q.input_type = "select"
                q.options = occupation_options if occupation_options else [
                    'Business', 'Construction Worker', 'Employment',
                    'Farmer', 'Journalist', 'Student',
                    'Unorganised Sector Worker', 'Other'
                ]
                break
        
        tagged_count = sum(1 for q in self.questions if q.occupation_category is not None)
        header_count = sum(1 for q in self.questions if q.is_category_header)
        print(f"Tagged {tagged_count} occupation sub-questions ({header_count} headers will be hidden)")
        print(f"Occupation options: {occupation_options}")

    def _set_district_and_block_options(self):
        """Set Q23 (district) as a select dropdown with all 38 Bihar districts,
        and Q22 (block) as a text field with placeholder."""
        bihar_districts = [
            "Araria", "Arwal", "Aurangabad", "Banka", "Begusarai",
            "Bhagalpur", "Bhojpur", "Buxar", "Darbhanga", "East Champaran (Motihari)",
            "Gaya", "Gopalganj", "Jamui", "Jehanabad", "Kaimur (Bhabua)",
            "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura",
            "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Nawada",
            "Patna", "Purnia", "Rohtas", "Saharsa", "Samastipur",
            "Saran (Chapra)", "Sheikhpura", "Sheohar", "Sitamarhi",
            "Siwan", "Supaul", "Vaishali", "West Champaran (Bettiah)"
        ]
        
        for q in self.questions:
            if q.id == "q_23":
                q.input_type = "select"
                q.options = bihar_districts
                print(f"Set Q23 with {len(bihar_districts)} Bihar districts")
                break

    def _reorder_questions(self):
        """Reorder questions:
        1. Move Q17 (marital status) + follow-ups before Q12 (children)
        2. Move Q19 (gender) + follow-ups to 3rd position (right after Q2)
        """
        # --- Step 1: Move Q17 before Q12 ---
        q17_group = []
        other_questions = []
        collecting_q17 = False
        
        for q in self.questions:
            if q.id == "q_17":
                collecting_q17 = True
                q17_group.append(q)
            elif collecting_q17 and q.question_type == "black" and q.parent_question == "q_17":
                q17_group.append(q)
            else:
                collecting_q17 = False
                other_questions.append(q)
        
        if q17_group:
            reordered = []
            inserted = False
            for q in other_questions:
                if q.id == "q_12" and not inserted:
                    reordered.extend(q17_group)
                    inserted = True
                reordered.append(q)
            if not inserted:
                reordered.extend(q17_group)
            self.questions = reordered
            print(f"Reordered: Marital status (Q17) now asked before children (Q12)")
        
        # --- Step 2: Move Q19 (gender) + follow-ups to after Q2 ---
        q19_group = []
        remaining = []
        collecting_q19 = False
        
        for q in self.questions:
            if q.id == "q_19":
                collecting_q19 = True
                q19_group.append(q)
            elif collecting_q19 and q.question_type == "black" and q.parent_question == "q_19":
                q19_group.append(q)
            else:
                collecting_q19 = False
                remaining.append(q)
        
        if q19_group:
            reordered2 = []
            inserted2 = False
            for q in remaining:
                reordered2.append(q)
                if q.id == "q_2" and not inserted2:
                    reordered2.extend(q19_group)
                    inserted2 = True
            if not inserted2:
                reordered2.extend(q19_group)
            self.questions = reordered2
            print(f"Reordered: Gender (Q19) now asked as 3rd question (after Q2)")
    
    def _load_schemes(self):
        """Load Bihar schemes from CSV file with detailed eligibility criteria.
        
        Each row has scheme_name, eligibility (JSON array of text criteria),
        plus details, benefits, application_process, documents_required, faqs.
        
        Each criterion is a natural-language sentence that we classify into
        a question ID + structured rule for matching against user answers.
        """
        import re
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(base_dir, 'data', 'schemes_criteria.csv')
            df = pd.read_csv(csv_path)
            
            for _, row in df.iterrows():
                scheme_name = row['scheme_name']
                
                # Parse eligibility JSON array
                try:
                    elig_list = json.loads(row['eligibility']) if pd.notna(row.get('eligibility')) else []
                except (json.JSONDecodeError, TypeError):
                    elig_list = []
                
                scheme = BiharScheme(
                    name=scheme_name,
                    description=str(row.get('details', ''))[:500] if pd.notna(row.get('details')) else '',
                )
                
                # Classify each criterion → (question_id, rule)
                for crit_text in elig_list:
                    result = self._classify_criterion(crit_text, scheme_name)
                    if result is None:
                        continue  # unmappable criterion
                    qid, rule = result
                    if qid not in scheme.eligibility_criteria:
                        scheme.eligibility_criteria[qid] = []
                    scheme.eligibility_criteria[qid].append(rule)
                
                if scheme.eligibility_criteria:
                    self.schemes.append(scheme)
            
            print(f"Loaded {len(self.schemes)} schemes from CSV with parsed eligibility criteria")
            
            # Stats
            total_rules = sum(
                sum(len(rules) for rules in s.eligibility_criteria.values())
                for s in self.schemes
            )
            print(f"Total parsed rules: {total_rules}")
            
            # Post-process: scan scheme names for hidden gender/occupation rules
            self._add_implicit_criteria_from_names()
            
        except Exception as e:
            print(f"Error loading schemes from CSV: {e}")
            import traceback
            traceback.print_exc()
            self._load_sample_schemes()
    
    def _add_implicit_criteria_from_names(self):
        """Scan scheme names for hidden gender/occupation keywords.
        
        Some schemes like 'Mukhyamantri Kanya Vivah Yojana' are clearly female-only
        but the eligibility text may not explicitly say 'female'. Same for farmer/student
        schemes. This catches those.
        """
        import re
        
        female_keywords = [
            'girl', 'woman', 'women', 'female', 'kanya', 'nari', 'mahila',
            'daughter', 'balika', 'kishori', 'adolescent girl',
        ]
        
        occ_keyword_map = {
            'Farmer': ['farmer', 'krishi', 'fasal', 'kisan', 'agriculture', 'crop', 'seed'],
            'Construction Worker': ['construction worker', 'bbocwwb', 'building worker'],
            'Student': ['student', 'vidyarthi', 'scholarship'],
            'Journalist': ['journalist', 'patrakar'],
        }
        
        gender_added = 0
        occ_added = 0
        
        for scheme in self.schemes:
            name_lower = scheme.name.lower()
            
            # --- Gender ---
            has_gender = 'q_19' in scheme.eligibility_criteria and any(
                r.get('type') == 'gender_match' for r in scheme.eligibility_criteria['q_19']
            )
            if not has_gender:
                if any(kw in name_lower for kw in female_keywords):
                    if 'q_19' not in scheme.eligibility_criteria:
                        scheme.eligibility_criteria['q_19'] = []
                    scheme.eligibility_criteria['q_19'].append({
                        'type': 'gender_match',
                        'accepted': ['Female'],
                        'desc': f'Female applicant (from scheme name: {scheme.name})'
                    })
                    gender_added += 1
            
            # --- Occupation ---
            has_occ = 'q_13' in scheme.eligibility_criteria and any(
                r.get('type') == 'occupation_match' for r in scheme.eligibility_criteria['q_13']
            )
            if not has_occ:
                detected = None
                for occ_name, keywords in occ_keyword_map.items():
                    if any(kw in name_lower for kw in keywords):
                        if detected is None:
                            detected = occ_name
                        elif detected != occ_name:
                            detected = None
                            break
                if detected:
                    if 'q_13' not in scheme.eligibility_criteria:
                        scheme.eligibility_criteria['q_13'] = []
                    scheme.eligibility_criteria['q_13'].append({
                        'type': 'occupation_match',
                        'accepted': [detected],
                        'desc': f'{detected} (from scheme name: {scheme.name})'
                    })
                    occ_added += 1
        
        if gender_added or occ_added:
            print(f"Added implicit criteria: {gender_added} gender, {occ_added} occupation rules")
    
    def _classify_criterion(self, text: str, scheme_name: str = '') -> Optional[tuple]:
        """Classify a single natural-language eligibility criterion.
        
        Returns (question_id, rule_dict) or None if unmappable.
        
        This is the core NLP parser that maps free-text criteria to our 28 questions.
        """
        import re
        c = text.lower().strip()
        full_context = (scheme_name + ' ' + text).lower()
        
        # ===== Q2: Bihar Resident =====
        if 'resident of bihar' in c or 'permanent resident' in c or ('resident' in c and 'bihar' in c):
            return ('q_2', {'type': 'yes', 'desc': text})
        
        # ===== Q19: Gender =====
        if re.search(r'\bfemale\b|\bwoman\b|\bwomen\b|\bgirl\b(?!.*school)|\bmale\b|transgender', c):
            # Detect which gender
            if re.search(r'\bfemale\b|\bwoman\b|\bwomen\b|\bgirl\b', c):
                if re.search(r'\bmale\b', c) and not re.search(r'\bfemale\b', c):
                    # "Both male and female" → info, not a gender filter
                    return None
                accepted = ['Female']
                if 'transgender' in c:
                    accepted.append('Other')
                return ('q_19', {'type': 'gender_match', 'accepted': accepted, 'desc': text})
            if re.search(r'\bmale\b', c) and not re.search(r'\bfemale\b', c):
                return ('q_19', {'type': 'gender_match', 'accepted': ['Male'], 'desc': text})
        
        # ===== Q15: Age =====
        if re.search(r'age[d ]|years? old|years? or above|years? or more|between \d+ and \d+.*year|age.*(limit|must|should|between|minimum)', c):
            # "between X and Y years"
            between = re.findall(r'between\s+(\d+)\s+(?:and|to|-)\s+(\d+)', c)
            if between:
                return ('q_15', {'type': 'age_range', 'min': int(between[0][0]), 'max': int(between[0][1]), 'desc': text})
            # "aged X to Y" or "age X-Y"
            aged = re.findall(r'aged?\s+(\d+)\s+(?:to|-)\s+(\d+)', c)
            if aged:
                return ('q_15', {'type': 'age_range', 'min': int(aged[0][0]), 'max': int(aged[0][1]), 'desc': text})
            # "X years or above/older/more"
            above = re.findall(r'(\d+)\s+(?:years?\s+)?(?:or\s+)?(?:above|older|more)', c)
            if above:
                return ('q_15', {'type': 'age_min', 'min': int(above[0]), 'desc': text})
            # "below/under X years" or "not more than X"
            below = re.findall(r'(?:not\s+more\s+than|below|under|less\s+than)\s+(\d+)', c)
            if below:
                return ('q_15', {'type': 'age_max', 'max': int(below[0]), 'desc': text})
            # Age limit with a range like "18-60"
            limit_range = re.findall(r'age.*?(\d+)\s*[-–to]+\s*(\d+)', c)
            if limit_range:
                return ('q_15', {'type': 'age_range', 'min': int(limit_range[0][0]), 'max': int(limit_range[0][1]), 'desc': text})
            # Fallback: any two numbers in age context
            nums = re.findall(r'\b(\d+)\b', c)
            if len(nums) >= 2:
                return ('q_15', {'type': 'age_range', 'min': int(nums[0]), 'max': int(nums[1]), 'desc': text})
            return None  # Can't parse age → skip
        
        # ===== Q13: Occupation =====
        if re.search(r'\bfarmer\b|cultivat|construction.*work|building.*work|\bworker\b.*craftsman|\bbbocwwb\b|unorgani[sz]ed.*sector|artisan', c):
            if 'farmer' in c or 'cultivat' in c:
                return ('q_13', {'type': 'occupation_match', 'accepted': ['Farmer'], 'desc': text})
            if 'construction' in c or 'building' in c or 'bbocwwb' in c:
                return ('q_13', {'type': 'occupation_match', 'accepted': ['Construction Worker'], 'desc': text})
            if 'unorganised' in c or 'unorganized' in c or ('worker' in c and 'craftsman' in c):
                return ('q_13', {'type': 'occupation_match', 'accepted': ['Unorganised Sector Worker'], 'desc': text})
            if 'artisan' in c:
                return ('q_13', {'type': 'occupation_match', 'accepted': ['Unorganised Sector Worker'], 'desc': text})
        
        if re.search(r'\bjournalist\b|media representative', c):
            return ('q_13', {'type': 'occupation_match', 'accepted': ['Journalist'], 'desc': text})
        
        if re.search(r'\bbusiness\b.*(?:unit|firm|proprietorship|partnership)|start.?up', c):
            return ('q_13', {'type': 'occupation_match', 'accepted': ['Business'], 'desc': text})
        
        # ===== Q20: Social Category =====
        if re.search(r'scheduled caste|scheduled tribe|\bsc\b|\bst\b|\bobc\b|\bbc\b|\bebc\b|backward class|extremely backward|general category', c):
            accepted = []
            cat_map = {
                'scheduled caste': 'SC', 'sc': 'SC',
                'scheduled tribe': 'ST', 'st': 'ST',
                'obc': 'OBC', 'other backward': 'OBC',
                'extremely backward': 'EBC', 'ebc': 'EBC', 'ati pichhada': 'EBC',
                'backward class': 'BC', 'bc': 'BC',
                'general': 'General',
            }
            for key, val in cat_map.items():
                if key in c and val not in accepted:
                    accepted.append(val)
            if accepted:
                return ('q_20', {'type': 'category_match', 'accepted': accepted, 'desc': text})
        
        # ===== Q1: Income =====
        if re.search(r'income|₹|rs\.\s*\d|annual.*family', c):
            amt_matches = re.findall(r'[\d,]+', text.replace('₹', '').replace('Rs.', '').replace('/-', ''))
            if amt_matches:
                # Take the largest number as the income limit
                vals = [int(a.replace(',', '')) for a in amt_matches if a.replace(',', '').isdigit()]
                if vals:
                    max_val = max(vals)
                    return ('q_1', {'type': 'income_max', 'max': max_val, 'desc': text})
        
        # ===== Q18: Economic Status (BPL/APL) =====
        if re.search(r'\bbpl\b|below poverty|poverty line|ultra.?poor|poor famil', c):
            if 'ultra' in c:
                return ('q_18', {'type': 'economic_match', 'accepted': ['Ultra-poor'], 'desc': text})
            return ('q_18', {'type': 'economic_match', 'accepted': ['Ultra-poor', 'below poverty line (BPL)'], 'desc': text})
        
        # ===== Q17: Marital Status =====
        if re.search(r'\bwidow\b|\bdivorced\b|\bunmarried\b|\bremarr|\binter.?caste\b|\bmarried\b', c):
            if 'remarr' in c and ('not' in c or 'ineligible' in c):
                return ('q_17', {'type': 'marital_not', 'rejected': ['Remarried'], 'desc': text})
            if 'inter-caste' in c or 'inter caste' in c:
                return None  # Special check we can't map to a simple select
            if 'widow' in c:
                if 'not eligible' in c:
                    return ('q_17', {'type': 'marital_not', 'rejected': ['Widowed'], 'desc': text})
                return ('q_17', {'type': 'marital_match', 'accepted': ['Widowed'], 'desc': text})
            if 'divorced' in c:
                return ('q_17', {'type': 'marital_match', 'accepted': ['Divorced'], 'desc': text})
            if 'unmarried' in c:
                return ('q_17', {'type': 'marital_match', 'accepted': ['Unmarried'], 'desc': text})
        
        # ===== Q7: Disability =====
        if re.search(r'\bdisab|\bdivyang|\bhandicap|\bblind|\bdeaf|\bimpairment', c):
            return ('q_7', {'type': 'yes', 'desc': text})
        
        # ===== Q11: Land =====
        if re.search(r'\bacre|\bland\b|\blandless\b|\bhectare\b|agricultural land', c):
            between = re.findall(r'(?:minimum|min)\s+([\d.]+)\s+(?:acres?\s+)?(?:and|to)?\s*(?:a\s+)?(?:maximum|max)?\s*([\d.]+)?', c)
            if between and between[0][1]:
                return ('q_11', {'type': 'range', 'min': float(between[0][0]), 'max': float(between[0][1]), 'desc': text})
            min_match = re.findall(r'minimum\s+([\d.]+)\s+acre', c)
            if min_match:
                return ('q_11', {'type': 'min_val', 'min': float(min_match[0]), 'desc': text})
            max_match = re.findall(r'maximum\s+([\d.]+)\s+acre', c)
            if max_match:
                return ('q_11', {'type': 'max_val', 'max': float(max_match[0]), 'desc': text})
            range_match = re.findall(r'([\d.]+)\s+acres?\s+.*?([\d.]+)\s+acres?', c)
            if range_match:
                return ('q_11', {'type': 'range', 'min': float(range_match[0][0]), 'max': float(range_match[0][1]), 'desc': text})
            if 'landless' in c:
                return ('q_11', {'type': 'max_val', 'max': 0, 'desc': text})
            return None  # Can't parse land criterion
        
        # ===== Q16: Education =====
        if re.search(r'10\+2|intermediate|matric|graduate|diploma|iti|polytechnic|education.*qualif|exam|upsc|bpsc|competitive|preliminary.*exam|passed.*exam', c):
            return None  # Education is too varied to enforce → skip (info only)
        
        # ===== Q4: DBT Registered =====
        if 'dbt' in c or 'direct benefit transfer' in c:
            return ('q_4', {'type': 'yes', 'desc': text})
        
        # ===== Q5: Bank Account =====
        if 'bank account' in c:
            return ('q_5', {'type': 'yes', 'desc': text})
        
        # ===== Q14: Aadhaar =====
        if 'aadhaar' in c or 'aadhar' in c:
            return ('q_14', {'type': 'yes', 'desc': text})
        
        # ===== Q6: Minority =====
        if 'minority' in c or 'muslim' in c:
            return ('q_6', {'type': 'yes', 'desc': text})
        
        # ===== Q3: Pension =====
        if re.search(r'pension|retired', c):
            if 'not' in c and ('receiving' in c or 'retired' in c or 'eligible' in c):
                return ('q_3', {'type': 'no', 'desc': text})
            return ('q_3', {'type': 'yes', 'desc': text})
        
        # ===== Q9: Death in Family =====
        if 'death' in c and ('family' in c or 'deceased' in c or 'natural death' in c):
            return ('q_9', {'type': 'yes', 'desc': text})
        
        # ===== Q10: Medical Condition =====
        if re.search(r'\bmedical\b|\bdisease\b|\bhealth\b|\btreatment\b|\baids\b', c):
            return ('q_10', {'type': 'yes', 'desc': text})
        
        # ===== Q24: Pregnant/Lactating =====
        if re.search(r'pregnan|lactating|breastfeeding|maternity|childbirth', c):
            return ('q_24', {'type': 'yes', 'desc': text})
        
        # ===== Q25: Fish Pond =====
        if re.search(r'\bfish\b|\bpond\b|\baquaculture\b', c):
            return ('q_25', {'type': 'yes', 'desc': text})
        
        # ===== Q27: Piped Water =====
        if 'piped water' in c or 'water supply' in c or 'drinking water' in c:
            return ('q_27', {'type': 'no', 'desc': text})  # No = they need it
        
        # ===== Q28: PMAY-G =====
        if 'pmay' in c or 'pradhan mantri awas' in c:
            return ('q_28', {'type': 'yes', 'desc': text})
        
        # ===== Q8: Driving License =====
        if 'driving' in c or 'license' in c:
            return ('q_8', {'type': 'yes', 'desc': text})
        
        # ===== Q12: Children =====
        if re.search(r'\bchild|\bdaughter|\bson\b|two.*girl|girl.*child|first.*born', c):
            return None  # Children criteria are too specific → skip
        
        # ===== Student detected from context (not from "student" keyword in occupation block above) =====
        if re.search(r'\bstudent\b|\bstudying\b|\benrolled\b.*\bcourse\b', c):
            return ('q_13', {'type': 'occupation_match', 'accepted': ['Student'], 'desc': text})
        
        # ===== Unmapped: return None =====
        return None
    
    def _load_sample_schemes(self):
        """Load sample Bihar schemes as fallback"""
        sample_schemes = [
            BiharScheme(
                name="Mukhyamantri Vridhjan Pension Yojana",
                eligibility_criteria={
                    "q_2": [{'type': 'yes', 'desc': 'Resident of Bihar'}],
                    "q_15": [{'type': 'age_min', 'min': 60, 'desc': 'Age 60+'}],
                    "q_1": [{'type': 'income_max', 'max': 60000, 'desc': 'Income <= 60000'}]
                },
                description="Old age pension scheme for elderly citizens of Bihar",
                benefits=["Monthly pension of ₹400-500"]
            ),
        ]
        self.schemes = sample_schemes
        print(f"Loaded {len(self.schemes)} sample schemes")
    
    def get_current_question(self) -> Optional[Question]:
        """Get the current question to display, skipping questions based on conditions"""
        while self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            
            # Check special skip rules (e.g., unmarried -> skip children)
            if self._should_skip_question(question):
                self.current_question_index += 1
                continue
            
            if question.question_type == "orange":
                return question
            elif question.question_type == "black":
                if self._should_show_black_question(question):
                    return question
                else:
                    # Skip this black question automatically
                    self.current_question_index += 1
                    continue
            else:
                return question
        
        return None
    
    def _should_skip_question(self, question: Question) -> bool:
        """Check if a question should be skipped based on special conditions"""
        marital_answer = self.user_responses.get("q_17")
        
        # If user is unmarried, skip children question (Q12) and its follow-ups
        if marital_answer and str(marital_answer).strip() == "Unmarried":
            if question.id == "q_12" or question.parent_question == "q_12":
                return True
        
        # If user is Male, skip pregnancy/lactating question (Q24) and its follow-ups
        gender_answer = self.user_responses.get("q_19")
        if gender_answer and str(gender_answer).strip() == "Male":
            if question.id == "q_24" or question.parent_question == "q_24":
                return True
        
        # Always skip Q21 (Where do you currently live?) and its follow-ups
        if question.id == "q_21" or question.parent_question == "q_21":
            return True
        
        # Always skip Q22 (block) and Q23 (district) — Bihar-only app
        if question.id in ("q_22", "q_23"):
            return True
        
        return False
    
    def _should_show_black_question(self, question: Question) -> bool:
        """Check if a black question should be shown based on parent question answer"""
        if not question.parent_question or question.parent_question not in self.user_responses:
            return False
        
        # Never show category headers (e.g., "Business", "Farmer" under Q13)
        if question.is_category_header:
            return False
        
        parent_answer = self.user_responses[question.parent_question]
        
        # Find the parent question object to check its input type
        parent_q = None
        for q in self.questions:
            if q.id == question.parent_question:
                parent_q = q
                break
        
        # --- Yes/No parent questions: follow-up only if "Yes" ---
        if parent_q and parent_q.input_type == "yes_no":
            return str(parent_answer).strip() == "Yes"
        
        # --- Occupation (Q13): show only sub-questions matching selected occupation ---
        if question.parent_question == "q_13":
            if not question.occupation_category:
                return False
            user_occupation = str(parent_answer).strip()
            return user_occupation.lower() == question.occupation_category.lower()
        
        # --- Marital status (Q17) follow-ups: show if NOT "Unmarried" ---
        if question.parent_question == "q_17":
            return str(parent_answer).strip() != "Unmarried"
        
        # --- Children (Q12) follow-ups: show if children count > 0 ---
        if question.parent_question == "q_12":
            try:
                return float(parent_answer) > 0
            except (ValueError, TypeError):
                return True
        
        # --- For other non-Yes/No parents (Q11 land, Q16 education, Q19 gender, Q21 living): ---
        # Show sub-questions if parent was answered (these are always relevant)
        return True
    
    def submit_answer(self, question_id: str, answer: Any) -> bool:
        """Submit an answer and move to next question"""
        self.user_responses[question_id] = answer
        self.current_question_index += 1
        return True
    
    # Questions that are skipped in the questionnaire (user won't have answers)
    SKIPPED_QUESTIONS = {'q_21', 'q_22', 'q_23'}
    
    def get_eligible_schemes(self) -> List[BiharScheme]:
        """Get eligible schemes based on user responses.
        
        Each scheme has eligibility_criteria = {qid: [rule, rule, ...]}
        A scheme is eligible ONLY if ALL real (non-info) criteria pass.
        - info-only criteria are ignored (they don't prove eligibility).
        - Skipped questions (Q21/Q22/Q23) are ignored.
        - If user didn't answer a question with real rules → not eligible.
        - Scheme must have at least 1 real criterion that actually matches.
        """
        eligible_schemes = []
        
        for scheme in self.schemes:
            is_eligible = True
            real_match_count = 0
            
            for qid, rules in scheme.eligibility_criteria.items():
                # Skip criteria for questions we removed from the questionnaire
                if qid in self.SKIPPED_QUESTIONS:
                    continue
                
                # Separate real rules from info-only rules
                non_info_rules = [r for r in rules if r.get('type') != 'info']
                
                # If all rules are info-only, skip this criterion entirely
                if not non_info_rules:
                    continue
                
                user_answer = self.user_responses.get(qid)
                
                if user_answer is None:
                    # User didn't answer but there are real rules → can't verify
                    is_eligible = False
                    break
                
                # Check if at least one non-info rule passes
                question_passes = any(
                    self._check_rule(qid, user_answer, rule) for rule in non_info_rules
                )
                
                if question_passes:
                    real_match_count += 1
                else:
                    is_eligible = False
                    break
            
            # Must be eligible AND have at least 1 real criterion matched
            if is_eligible and real_match_count > 0:
                eligible_schemes.append(scheme)
        
        return eligible_schemes
    
    def _check_rule(self, qid: str, user_answer: Any, rule: Dict[str, Any]) -> bool:
        """Check a single eligibility rule against the user's answer."""
        rtype = rule.get('type', 'info')
        answer = str(user_answer).strip()
        
        if rtype == 'info':
            return True
        
        if rtype == 'yes':
            return answer == 'Yes'
        
        if rtype == 'no':
            return answer == 'No'
        
        if rtype == 'age_range':
            try:
                age = float(answer)
                return rule['min'] <= age <= rule['max']
            except (ValueError, TypeError):
                return False
        
        if rtype == 'age_min':
            try:
                return float(answer) >= rule['min']
            except (ValueError, TypeError):
                return False
        
        if rtype == 'age_max':
            try:
                return float(answer) <= rule['max']
            except (ValueError, TypeError):
                return False
        
        if rtype == 'income_max':
            try:
                return float(answer) <= rule['max']
            except (ValueError, TypeError):
                return False
        
        if rtype in ('category_match', 'gender_match', 'economic_match',
                      'marital_match', 'occupation_match'):
            accepted = [a.lower() for a in rule.get('accepted', [])]
            user_val = answer.lower()
            
            # Normalize occupation names so Excel values match dropdown options
            if rtype == 'occupation_match':
                occ_normalize = {
                    'journalist or media representative': 'journalist',
                    'unorganised sector worker / craftsman': 'unorganised sector worker',
                    'business startup': 'business',
                }
                accepted = [occ_normalize.get(a, a) for a in accepted]
            
            return user_val in accepted
        
        if rtype == 'marital_not':
            rejected = [r.lower() for r in rule.get('rejected', [])]
            return answer.lower() not in rejected
        
        if rtype == 'marital_check':
            # These need follow-up question answers; pass for now
            return True
        
        if rtype == 'range':
            try:
                val = float(answer)
                return rule.get('min', 0) <= val <= rule.get('max', float('inf'))
            except (ValueError, TypeError):
                return False
        
        if rtype == 'min_val':
            try:
                return float(answer) >= rule['min']
            except (ValueError, TypeError):
                return False
        
        if rtype == 'max_val':
            try:
                return float(answer) <= rule['max']
            except (ValueError, TypeError):
                return False
        
        # Unknown rule type → pass
        return True
    
    def _matches_criteria(self, user_answer: Any, required_value: str) -> bool:
        """Legacy criteria matching (kept for backward compatibility)."""
        user_str = str(user_answer).strip()
        required_str = str(required_value).strip()
        
        if user_str.lower() == required_str.lower():
            return True
        
        return False
    
    def is_complete(self) -> bool:
        """Check if questionnaire is complete"""
        return self.get_current_question() is None
    
    def get_progress(self) -> Dict[str, Any]:
        """Get questionnaire progress information.
        Calculates visible questions (not hidden sub-questions) for accurate progress."""
        completed_questions = len(self.user_responses)
        
        # Count questions that will actually be shown to the user
        visible_count = 0
        for q in self.questions:
            # Always count main (orange) questions
            if q.question_type == "orange":
                # Skip if this question would be skipped by special rules
                if not self._should_skip_question(q):
                    visible_count += 1
            elif q.question_type == "black":
                # Skip category headers
                if q.is_category_header:
                    continue
                # Count sub-questions that are currently visible
                if self._should_show_black_question(q):
                    visible_count += 1
        
        # Ensure we show at least the main question count as minimum
        main_count = sum(1 for q in self.questions if q.question_type == 'orange')
        visible_count = max(visible_count, main_count)
        
        return {
            "total_questions": visible_count,
            "completed_questions": completed_questions, 
            "percentage": (completed_questions / max(visible_count, 1)) * 100,
            "current_question_index": self.current_question_index
        }
    
    def reset(self):
        """Reset the questionnaire to start over"""
        self.user_responses = {}
        self.current_question_index = 0
    
    def export_responses(self) -> Dict[str, Any]:
        """Export user responses for saving/loading"""
        return {
            "responses": self.user_responses,
            "current_index": self.current_question_index
        }
    
    def import_responses(self, data: Dict[str, Any]):
        """Import saved responses"""
        self.user_responses = data.get("responses", {})
        self.current_question_index = data.get("current_index", 0)


# Example usage and testing
if __name__ == "__main__":
    questionnaire = BiharQuestionnaire()
    
    print("Bihar Questionnaire System Loaded")
    print(f"Total questions: {len(questionnaire.questions)}")
    print(f"Total schemes: {len(questionnaire.schemes)}")
    
    # Test the questionnaire flow
    print("\nTesting questionnaire flow:")
    current_q = questionnaire.get_current_question()
    if current_q:
        print(f"First question: {current_q.text}")
        print(f"Question type: {current_q.question_type}")
        print(f"Options: {current_q.options}")