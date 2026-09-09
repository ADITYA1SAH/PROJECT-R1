"""
Query Rewriter for PROJECT R1
Fixes typos, expands abbreviations, and normalises input
"""

import re

# Common typos and corrections
TYPO_MAP = {
    "ruth": "route",
    "recieve": "receive",
    "teh": "the",
    "thier": "their",
    "wat": "what",
    "wats": "what's",
    "whos": "who's",
    "ur": "your",
    "u": "you",
    "becuase": "because",
    "befor": "before",
    "dont": "don't",
    "didnt": "didn't",
    "isnt": "isn't",
    "wasnt": "wasn't",
    "wont": "won't",
    "wouldnt": "wouldn't",
    "couldnt": "couldn't",
    "shouldnt": "shouldn't",
    "havent": "haven't",
    "hasnt": "hasn't",
    "hadnt": "hadn't",
    "doesnt": "doesn't",
    "cuz": "because",
    "plz": "please",
    "pls": "please",
    "thx": "thanks",
    "ty": "thank you",
}

def rewrite_query(query):
    """
    Clean up common typos and expand abbreviations.
    """
    query = query.lower().strip()
    
    # Fix common typos (whole word only)
    for wrong, correct in TYPO_MAP.items():
        query = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, query)
    
    # Expand common abbreviations
    query = query.replace("whats", "what is")
    query = query.replace("whos", "who is")
    query = query.replace("wheres", "where is")
    query = query.replace("hows", "how is")
    query = query.replace("whys", "why is")
    
    # Fix repeated characters (e.g., "heelllooo" → "hello")
    query = re.sub(r'(.)\1{2,}', r'\1\1', query)
    
    return query