# Configuration file for Scheme Finder

# Application Settings
APP_NAME = "Government Scheme Finder"
VERSION = "1.0.0"
AUTHOR = "Your Name"

# Data Settings
DATA_FILE = "data/schemes_data.csv"

# Matching Settings
MIN_SCORE_THRESHOLD = 40.0  # Minimum score to consider a scheme eligible
TOP_SCHEMES_LIMIT = 10      # Number of top schemes to show

# Score Weights (Total should be 100)
WEIGHTS = {
    'age': 20,
    'gender': 15,
    'category': 15,
    'occupation': 15,
    'income': 10,
    'bpl': 10,
    'disability': 10,
    'keywords': 5
}

# Districts in Bihar
BIHAR_DISTRICTS = [
    "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Bhojpur",
    "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj", "Jamui",
    "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai",
    "Madhepura", "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Nawada",
    "Patna", "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura",
    "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali", "West Champaran"
]

# Categories
SOCIAL_CATEGORIES = ["General", "EWS", "BC", "EBC", "SC", "ST"]

# Occupations
OCCUPATIONS = [
    "Student",
    "Farmer",
    "Construction Worker",
    "Entrepreneur/Business Owner",
    "Fisherman",
    "Unorganized Sector Worker",
    "Artisan/Craftsman",
    "Unemployed",
    "Other"
]

# Education Levels
EDUCATION_LEVELS = [
    "Below 10th",
    "10th/Matriculation",
    "12th/Intermediate",
    "ITI/Polytechnic Diploma",
    "Graduate",
    "Post-Graduate"
]

# Report Settings
REPORT_OUTPUT_DIR = "reports"
REPORT_FORMAT = "txt"  # Can be extended to PDF, HTML in future
