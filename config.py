"""
Configuration and Constants for Mutual Funds Dashboard
"""

# Application Settings
APP_TITLE = "Pakistan Mutual Funds Dashboard"
APP_ICON = "📊"
APP_LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# Pagination Settings
ITEMS_PER_PAGE = 50

# Risk Level Configuration
RISK_ORDER = ['Very Low', 'Low', 'Medium', 'High']

# Risk Rating Mappings
RISK_RATING_MAPPINGS = {
    'very_low': ['aaa(f)', 'aaa', 'aa+(f)', 'aa+'],
    'low': ['aa(f)', 'aa', 'aa-(f)', 'aa-'],
    'medium': ['a+(f)', 'a+', 'a(f)', 'a'],
    'high': ['a-(f)', 'a-', 'bbb(f)', 'bbb', 'bbb+(f)', 'bbb+', 'bbb-(f)', 'bbb-', 'bb(f)', 'bb', 'b(f)', 'b']
}

# Data Folder
DATA_FOLDER = "data"
CLEANED_CSV_NAME = "funds_clean.csv"

# Column Detection Keywords
COLUMN_KEYWORDS = {
    'fund_name': ['fund', 'name'],
    'company': ['company', 'amc'],
    'nav': ['nav'],
    'category': ['category'],
    'risk': ['risk', 'rating'],
    'offer_price': ['offer', 'price']
}

# NAV Range Defaults
NAV_RANGE_DEFAULT = [0, 100]
