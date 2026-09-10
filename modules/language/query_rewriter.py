"""
Query Rewriter for PROJECT R1
Uses contractions library for automatic expansion
No hardcoded contraction maps needed
"""

import re
import contractions

# Only keep true typo corrections (not contractions)
TYPO_MAP = {
    "ruth": "route",
    "recieve": "receive",
    "teh": "the",
    "thier": "their",
    "wat": "what",
    "becuase": "because",
    "befor": "before",
    "cuz": "because",
    "plz": "please",
    "pls": "please",
    "thx": "thanks",
    "ur": "your",
    "u": "you",
}

def rewrite_query(query):
    """
    Clean up typos, expand contractions automatically, and normalise input.
    """
    query = query.lower().strip()
    
    # Fix true typos (whole word only)
    for wrong, correct in TYPO_MAP.items():
        query = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, query)
    
    # Expand ALL contractions automatically using contractions library
    # Handles: whats → what is, whos → who is, hows → how is,
    # wheres → where is, dont → don't, cant → can't, and hundreds more
    query = contractions.fix(query)
    
    # Fix repeated characters (e.g., "heelllooo" → "hello")
    query = re.sub(r'(.)\1{2,}', r'\1\1', query)
    
    return query