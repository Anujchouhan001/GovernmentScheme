# Section-Based Conditional Questionnaire System

## Overview

This system implements a **conditional, section-based questionnaire** where questions are organized into logical sections (A, B, C, etc.). Each section must be completed before the next section becomes available, and sections are only shown if their conditions are met.

## Key Features

### 1. **Section-Based Flow**
- Questions are grouped into logical sections (e.g., Basic Info, Economic Status, Occupation)
- Users complete one section at a time
- Progress is tracked and displayed

### 2. **Conditional Logic**
- Sections only appear if their conditions are satisfied
- For example:
  - **Section B (Economic Status)** only shows if user is from Bihar
  - **Section E (Farmer Details)** only shows if user is a farmer
  - **Section F (Construction Worker)** only shows if user is a construction worker

### 3. **Smart Question Flow**
- Questions within a section can have their own conditions
- Required vs optional questions
- Type-specific inputs (text, number, yes/no, select)

## How It Works

### Section Structure

Each section contains:
- **ID**: Unique identifier
- **Name**: Display name (e.g., "Section A: Basic Information")
- **Description**: What this section is about
- **Order**: Sequence number
- **Conditions**: Rules to unlock this section
- **Questions**: List of questions in this section

### Example Flow

```
START
  ↓
Section A: Basic Information
  ├─ State? (Bihar/Other)
  ├─ Age?
  ├─ Gender?
  └─ Category?
  ↓
[If state == Bihar]
  ↓
Section B: Economic Status
  ├─ Annual Income?
  ├─ BPL Card?
  ├─ Ultra Poor?
  └─ Rural Area?
  ↓
[If age >= 18]
  ↓
Section C: Occupation
  ├─ Occupation?
  ├─ Are you a farmer?
  ├─ Construction worker?
  └─ Student?
  ↓
[If is_farmer == Yes]
  ↓
Section E: Farmer Details
  ├─ DBT Registered?
  ├─ Land owned?
  └─ Crop damage?
  
[If is_construction_worker == Yes]
  ↓
Section F: Construction Worker Details
  ├─ BBOCWWB Registered?
  ├─ Membership years?
  └─ Active membership?
  
... and so on
```

## File Structure

```
SchemePy/
├── app_sectioned.py                    # Flask app with sectioned flow
├── src/
│   └── sectioned_questionnaire.py     # Core questionnaire logic
├── templates/
│   ├── sectioned_questionnaire.html   # Section display template
│   └── sectioned_results.html         # Results display
```

## Usage

### Running the Application

```bash
# Install dependencies
pip install flask

# Run the sectioned questionnaire app
python app_sectioned.py
```

The app will run on `http://localhost:5001`

### User Flow

1. **Start**: User clicks "Start Questionnaire"
2. **Section A**: Answer basic questions (always shown)
3. **Conditional Sections**: Based on answers, relevant sections appear
4. **Navigation**: "Continue" button after completing each section
5. **Results**: Summary of all responses at the end

## Sections Included

| Section | Name | Condition | Questions |
|---------|------|-----------|-----------|
| A | Basic Information | Always shown | State, Age, Gender, Category |
| B | Economic Status | State == Bihar | Income, BPL, Ultra Poor, Rural Area |
| C | Occupation | Age >= 18 | Occupation type, Farmer?, Worker?, Student? |
| D | Land & Property | is_farmer == True | Land acres, House ownership |
| E | Farmer Details | is_farmer == True | DBT, Crop damage |
| F | Construction Worker | is_construction_worker == True | BBOCWWB registration, membership |
| G | Education Details | is_student == True | Education level, 10th/12th status |
| H | Family Information | Always shown | Marital status, children |
| I | Identity Documents | Always shown | Aadhaar, bank account |
| J | Health & Disability | Always shown | Disability, medical conditions |

## Customization

### Adding a New Section

```python
new_section = Section(
    id="section_k",
    name="Section K: New Topic",
    description="Description of what this section covers",
    order=11,
    conditions=[
        {"field": "some_field", "operator": "equals", "value": "some_value"}
    ],
    questions=[
        Question(
            id="question_1",
            text="Your question text?",
            type="yes_no",  # or "text", "number", "select"
            required=True
        )
    ]
)
```

### Condition Operators

- `equals`: Exact match
- `!=`: Not equal
- `>`, `>=`, `<`, `<=`: Numeric comparisons
- `in`: Value in list
- `not_in`: Value not in list

### Complex Conditions

```python
conditions=[
    # ALL conditions must be true
    {"all": [
        {"field": "age", "operator": ">=", "value": 18},
        {"field": "state", "operator": "equals", "value": "Bihar"}
    ]},
    # OR at least ONE must be true
    {"any": [
        {"field": "is_farmer", "operator": "equals", "value": True},
        {"field": "occupation", "operator": "equals", "value": "Farmer"}
    ]}
]
```

## Question Types

### 1. Text Input
```python
Question(
    id="name",
    text="What is your name?",
    type="text"
)
```

### 2. Number Input
```python
Question(
    id="age",
    text="What is your age?",
    type="number"
)
```

### 3. Yes/No
```python
Question(
    id="has_aadhaar",
    text="Do you have an Aadhaar card?",
    type="yes_no"
)
```

### 4. Select Dropdown
```python
Question(
    id="state",
    text="Which state?",
    type="select",
    options=["Bihar", "Other"]
)
```

## API Endpoints

### Get Questionnaire State
```
GET /api/questionnaire/state
Response: {
  "sections": [...],
  "current_section_id": "section_a",
  "user_responses": {...},
  "progress": {
    "total_sections": 10,
    "completed_sections": 3,
    "progress_percentage": 30
  }
}
```

### Validate Section
```
POST /api/section/validate
Body: {
  "section_id": "section_a",
  "responses": {...}
}
Response: {
  "is_complete": true,
  "section_id": "section_a"
}
```

## Benefits of This Approach

1. **✅ User-Friendly**: One section at a time reduces cognitive load
2. **✅ Efficient**: Only relevant questions are shown
3. **✅ Progress Tracking**: Users see how far they've come
4. **✅ Flexible**: Easy to add/modify sections and conditions
5. **✅ Validation**: Section-wise validation before proceeding
6. **✅ Session Management**: Responses saved across sections

## Integration with Scheme Matching

After collecting all responses, you can:

1. Load the scheme eligibility data
2. Match user responses against scheme criteria
3. Return only schemes where ALL conditions are met (100% match)

```python
# Example integration
from src.sectioned_questionnaire import SectionedQuestionnaire
from src.eligibility_checker import EligibilityChecker

# After questionnaire completion
questionnaire = SectionedQuestionnaire()
user_responses = questionnaire.user_responses

# Match with schemes
checker = EligibilityChecker(schemes)
eligible_schemes = checker.find_100_percent_matches(user_responses)
```

## Future Enhancements

- [ ] Save progress to database
- [ ] Allow going back to previous sections
- [ ] Export responses as PDF
- [ ] Multi-language support
- [ ] Accessibility improvements
- [ ] Mobile-responsive design
- [ ] Real-time validation
- [ ] Skip logic within sections

## License

This is part of the SchemePy project for finding eligible government schemes in Bihar.
