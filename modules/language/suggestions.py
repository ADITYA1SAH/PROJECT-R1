"""
"Did you mean?" suggestions for PROJECT R1
"""

import difflib

# Common commands and phrases
COMMON_PHRASES = [
    "what is my name",
    "what is the weather",
    "show memory",
    "help",
    "version",
    "exit",
    "mode normal",
    "mode professional",
    "mode idle",
    "mode emergency",
    "remember my name is",
    "where do I live",
    "what is my favorite color",
]

def suggest_correction(query):
    """
    Return the closest matching command or phrase.
    """
    query = query.lower().strip()
    matches = difflib.get_close_matches(query, COMMON_PHRASES, n=1, cutoff=0.6)
    if matches:
        return matches[0]
    return None