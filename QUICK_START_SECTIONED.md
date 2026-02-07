# Quick Start: Section-Based Questionnaire

## What I Created

I've built a **section-based conditional questionnaire system** where:

1. ✅ Questions are organized into **sections** (A, B, C, etc.)
2. ✅ Users answer **one section at a time**
3. ✅ Next sections **unlock only if conditions are met**
4. ✅ Progress is tracked throughout the flow
5. ✅ Only relevant questions are shown

## Files Created

```
📁 SchemePy/
├── 📄 app_sectioned.py                          # Flask app with sectioned flow
├── 📄 demo_sectioned.py                         # Demo script showing how it works
├── 📁 src/
│   └── 📄 sectioned_questionnaire.py           # Core questionnaire logic
├── 📁 templates/
│   ├── 📄 sectioned_questionnaire.html         # Question display page
│   └── 📄 sectioned_results.html               # Results summary page
└── 📁 docs/
    └── 📄 SECTIONED_QUESTIONNAIRE_GUIDE.md     # Detailed documentation
```

## How to Run

### Option 1: Run the Demo (Console)
```bash
python demo_sectioned.py
```

This will show you how the conditional logic works in the console.

### Option 2: Run the Web App
```bash
python app_sectioned.py
```

Then open: http://localhost:5001

## How It Works - Example Flow

```
┌─────────────────────────────────────┐
│  Section A: Basic Information      │
│  ✓ Always shown first               │
├─────────────────────────────────────┤
│  1. Which state? → Bihar           │
│  2. Age? → 25                      │
│  3. Gender? → Male                 │
│  4. Category? → General            │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Section B: Economic Status         │
│  ✓ Unlocked (state == Bihar)       │
├─────────────────────────────────────┤
│  1. Annual Income? → ₹50,000       │
│  2. BPL Card? → Yes                │
│  3. Ultra Poor? → No               │
│  4. Rural Area? → Yes              │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Section C: Occupation              │
│  ✓ Unlocked (age >= 18)            │
├─────────────────────────────────────┤
│  1. Occupation? → Farmer           │
│  2. Are you farmer? → Yes          │
│  3. Construction worker? → No      │
│  4. Student? → No                  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Section E: Farmer Details          │
│  ✓ Unlocked (is_farmer == Yes)     │
├─────────────────────────────────────┤
│  1. DBT Registered? → Yes          │
│  2. Land owned? → 2 acres          │
│  3. Crop damage? → 30%             │
└─────────────────────────────────────┘
         │
         ▼
    [Results Page]
```

## Key Features

### 1. Conditional Sections
Sections only appear if conditions are met:

```python
Section B: Economic Status
  Condition: state == "Bihar"
  
Section E: Farmer Details
  Condition: is_farmer == True
  
Section F: Construction Worker
  Condition: is_construction_worker == True
```

### 2. Progress Tracking
Users see:
- Current section number
- Total sections
- Progress percentage
- Completed sections count

### 3. Validation
Each section validates:
- Required fields are filled
- Correct data types
- Before allowing to continue

## Integration with Scheme Matching

After the questionnaire is complete, you can match responses with schemes:

```python
# Get user responses
user_responses = questionnaire.user_responses

# Example responses:
# {
#   "state": "Bihar",
#   "age": 25,
#   "is_farmer": True,
#   "land_owned_acres": 2,
#   "dbt_registered": True,
#   ...
# }

# Match with schemes (to be integrated)
eligible_schemes = match_schemes(user_responses)
```

## Customization

### Add a New Section

Edit `src/sectioned_questionnaire.py`:

```python
new_section = Section(
    id="section_new",
    name="Section K: Your Topic",
    description="What this section is about",
    order=11,
    conditions=[
        {"field": "some_field", "operator": "equals", "value": "some_value"}
    ],
    questions=[
        Question(
            id="your_question",
            text="Your question text?",
            type="yes_no"
        )
    ]
)

# Add to sections list
self.sections.append(new_section)
```

### Add a New Question to Existing Section

```python
# Find the section in _load_sections()
section_a.questions.append(
    Question(
        id="new_field",
        text="Your new question?",
        type="text",
        required=True
    )
)
```

## Next Steps

1. **Test the Demo**
   ```bash
   python demo_sectioned.py
   ```

2. **Run the Web App**
   ```bash
   python app_sectioned.py
   ```

3. **Customize Sections**
   - Edit `src/sectioned_questionnaire.py`
   - Add/modify sections and questions

4. **Integrate with Schemes**
   - Load your Excel/JSON scheme data
   - Map user responses to scheme eligibility criteria
   - Return matching schemes

## Benefits

✅ **User-Friendly**: One section at a time, not overwhelming
✅ **Efficient**: Only show relevant questions
✅ **Smart**: Conditional logic based on previous answers
✅ **Visual**: Progress bar shows completion
✅ **Flexible**: Easy to add new sections and questions

## Questions?

Read the full guide: `docs/SECTIONED_QUESTIONNAIRE_GUIDE.md`

---

**Created**: February 2026
**Purpose**: Bihar Government Scheme Finder - Sectioned Questionnaire System
