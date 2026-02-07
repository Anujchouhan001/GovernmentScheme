# User Guide - Government Scheme Finder

## Table of Contents
1. [Getting Started](#getting-started)
2. [Using the Application](#using-the-application)
3. [Understanding Results](#understanding-results)
4. [Tips for Best Results](#tips-for-best-results)
5. [Troubleshooting](#troubleshooting)

## Getting Started

### First Time Setup

1. **Open Terminal/Command Prompt**
   - Windows: Press `Win + R`, type `cmd`, press Enter
   - Navigate to project folder:
     ```
     cd c:\Users\canuj\OneDrive\Desktop\SchemePy
     ```

2. **Run the Application**
   ```
   python main.py
   ```

3. **You'll see the Main Menu**
   ```
   ================================================================================
                       MAIN MENU
   ================================================================================
   1. Find Schemes (Complete Questionnaire)
   2. Quick Find (Essential Questions Only)
   3. View All Schemes
   4. Search Scheme by Name
   5. Exit
   ================================================================================
   ```

## Using the Application

### Option 1: Find Schemes (Recommended)

**Best for**: Getting comprehensive, personalized scheme recommendations

**Steps**:
1. Select option `1` from main menu
2. Answer questions across 5 sections:
   - Basic Demographics (state, age, gender, category)
   - Professional Status (occupation, business details)
   - Education (qualification, competitive exams)
   - Financial & Social (income, BPL, disability, marital status)
   - Location (district)

3. View your personalized results
4. Optionally save report to file
5. View detailed information for specific schemes

**Example**:
```
What is your current age?
> 30

What is your gender?
  1. Male
  2. Female
  3. Transgender

Enter choice (1-3): 1
```

### Option 2: Quick Find

**Best for**: Getting quick results with minimal questions

**Steps**:
1. Select option `2`
2. Answer 6 essential questions only:
   - Age
   - Gender
   - Category
   - Occupation
   - Annual Income
3. Get top 5 matching schemes instantly

### Option 3: View All Schemes

**Best for**: Browsing all available schemes

**Steps**:
1. Select option `3`
2. See complete list of 106 schemes
3. Enter scheme number to view full details

### Option 4: Search by Name

**Best for**: Finding information about a specific scheme

**Steps**:
1. Select option `4`
2. Enter scheme name (partial match works)
3. View complete scheme details

## Understanding Results

### Match Score

Schemes are scored from 0-100:

- **90-100**: Excellent match ⭐⭐⭐⭐⭐
- **75-89**: Very good match ⭐⭐⭐⭐
- **60-74**: Good match ⭐⭐⭐
- **50-59**: Fair match ⭐⭐
- **40-49**: Moderate match ⭐

### What Each Score Means

**High Score (75+)**
- You meet most eligibility criteria
- High chance of approval
- Recommended to apply

**Medium Score (50-74)**
- You meet several criteria
- Review detailed eligibility
- May need additional documents

**Low Score (40-49)**
- Borderline eligibility
- Check all requirements carefully
- Consider alternatives

### Report Sections

**User Profile Summary**
- Your provided information
- Quick reference for verification

**Eligible Schemes**
- Ranked by match score
- Why you're eligible (match reasons)
- Key benefits
- Direct link for more info

**Detailed View**
- Complete scheme description
- All benefits
- Full eligibility criteria
- Required documents
- Step-by-step application process
- FAQs

## Tips for Best Results

### 1. Provide Accurate Information

❌ **Don't**:
- Round your age or income
- Guess your category
- Approximate land size

✅ **Do**:
- Use exact values
- Check documents for accuracy
- Be honest about status

### 2. Complete All Questions

Even if optional, answering all questions improves matching accuracy.

### 3. Understand Your Category

**General**: No caste-based reservation
**EWS**: Economically Weaker Section (income < ₹8 lakh)
**BC**: Backward Class
**EBC**: Extremely Backward Class
**SC**: Scheduled Caste
**ST**: Scheduled Tribe

### 4. Income Calculation

Include **all** family income sources:
- Salary/wages
- Agricultural income
- Business profits
- Pension
- Rental income

### 5. Check Documents

Before applying to any scheme, ensure you have:
- Aadhaar Card
- Residence Proof
- Income Certificate
- Caste Certificate (if applicable)
- Education Certificates
- Bank Account details

## Troubleshooting

### Problem: "CSV file not found"

**Solution**:
```
1. Check if 'data' folder exists
2. Verify 'schemes_data.csv' is in 'data' folder
3. Run from correct directory: cd SchemePy
```

### Problem: Invalid Input Error

**Solution**:
- For age: Enter only numbers (e.g., 25)
- For income: Don't use ₹ symbol or commas
- For choices: Enter the number, not the text

### Problem: No Schemes Found

**Possible Reasons**:
1. Age outside all scheme ranges
2. Income too high
3. State not Bihar (most schemes are Bihar-specific)

**Solution**:
- Review your inputs
- Try Quick Find mode
- Browse all schemes manually (Option 3)

### Problem: Application Freezes

**Solution**:
1. Press `Ctrl + C` to stop
2. Restart: `python main.py`
3. If persists, check Python version: `python --version`
   (Should be 3.8+)

### Problem: Can't See Full Text

**Solution**:
- Maximize terminal window
- On Windows: Right-click title bar → Properties → Layout
- Set Screen Buffer Width to 120

## Saving Reports

When asked "Save report?":
- Enter `y` or `yes` to save
- File saved as: `scheme_report_YYYYMMDD_HHMMSS.txt`
- Location: Same folder as main.py
- Open with Notepad or any text editor

## Getting Help

### In-Application Help
- Most questions have examples
- Error messages guide corrections
- Menu is always available

### For Technical Issues
- Check README.md for common issues
- Verify Python installation
- Ensure all files are present

## Best Practices

### For Students (Competitive Exams)
Focus on: Education schemes, Scholarship programs

### For Farmers
Focus on: Agricultural schemes, Subsidy programs

### For Entrepreneurs
Focus on: Startup schemes, Loan programs

### For Socially Disadvantaged
Check: SC/ST schemes, BPL schemes, Widow pensions

### For Senior Citizens
Look for: Pension schemes, Social security programs

## Next Steps After Finding Schemes

1. **Review Scheme Details**
   - Read full eligibility
   - Check all documents required
   - Note application deadlines

2. **Prepare Documents**
   - Gather all required papers
   - Get certificates attested
   - Make photocopies

3. **Apply**
   - Visit official website (link in report)
   - Follow application process
   - Submit before deadline

4. **Track Application**
   - Save application number
   - Check status regularly
   - Keep acknowledgment receipt

## Frequently Asked Questions

**Q: Can I apply to multiple schemes?**
A: Yes! Apply to all eligible schemes.

**Q: Is this the official government website?**
A: No, this is a helper tool. Apply through official links provided.

**Q: How often is the database updated?**
A: Data is from January 2026. Check official websites for latest info.

**Q: Can I use this for states other than Bihar?**
A: Currently optimized for Bihar schemes only.

**Q: What if my scheme is not listed?**
A: Database contains 106 major schemes. New schemes are added by government regularly.

**Q: Is my information saved?**
A: No, information is only used during the session and not stored.

---

**Need more help?** Contact your local government office or visit [MyScheme.gov.in](https://www.myscheme.gov.in)
