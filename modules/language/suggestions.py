"""
"Did you mean?" suggestions for PROJECT R1
Using TheFuzz for intelligent fuzzy matching
"""

from thefuzz import process, fuzz

# Core commands that need auto-correct
COMMAND_LIST = [
    "show memory",
    "version",
    "exit",
    "mode normal",
    "mode professional",
    "mode idle",
    "mode emergency",
]


def suggest_correction(query):
    """
    Only auto-correct if similarity is VERY high (95%+).
    This prevents general knowledge questions from being auto-corrected.
    """
    query = query.lower().strip()
    
    # Don't auto-correct if the query has more than 5 words
    if len(query.split()) > 5:
        return None
    
    # Don't auto-correct if the query contains location keywords
    location_keywords = ["in", "at", "near", "for"]
    if any(word in query.split() for word in location_keywords):
        return None
    
    # Use a very high cutoff (95%) — only true typos get corrected
    result = process.extractOne(query, COMMAND_LIST, scorer=fuzz.ratio, score_cutoff=95)
    if result:
        return result[0]
    return None