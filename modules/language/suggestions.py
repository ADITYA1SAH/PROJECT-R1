"""
"Did you mean?" suggestions for PROJECT R1
Using TheFuzz for intelligent fuzzy matching
"""

from thefuzz import process

# Core commands and common phrases
COMMAND_LIST = [
    "show memory",
    "version",
    "exit",
    "mode normal",
    "mode professional",
    "mode idle",
    "mode emergency",
    "remember my name is",
    "where do I live",
    "what is my school",
    "when is my birthday",
    "do i have a pet",
    "what is my city",
    "what is my country",
    "what is the weather",
]

def suggest_correction(query):
    """
    Return the closest matching command or phrase using TheFuzz.
    """
    query = query.lower().strip()
    
    # Skip correction for these common questions
    skip_phrases = [
        "what is gravity",
        "what is the capital",
        "who is",
        "what are you",
        "how are you",
        "who are you",
        "what can you do",
        "who created you",
        "what is your name",
        "wat",
        "hello",
        "hi",
        "hey",
    ]
    for phrase in skip_phrases:
        if phrase in query:
            return None
    
    # Use TheFuzz to find the best match
    result = process.extractOne(query, COMMAND_LIST, score_cutoff=80)
    if result:
        return result[0]  # Return the matched phrase
    return None