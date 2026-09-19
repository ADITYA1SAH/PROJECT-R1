"""
Personal Question Grounding for PROJECT R1
Determines if a question is about Aditya's personal facts
"""

import re
from modules.memory.memory import get_all_memory


# =========================
# STRICT PERSONAL PATTERNS
# =========================
# Only questions that ask about "my X" or "about me" — NOT "my" as substring

PERSONAL_PATTERNS = [
    # Direct personal questions
    r"\bmy\b",                    # "my name", "my dad" — whole word "my"
    r"\babout me\b",
    r"\bfor me\b",
    r"\bwho am i\b",
    r"\btell me about myself\b",
    r"\btell me about me\b",
    r"\bwhat do you know about me\b",
    # Recall commands
    r"\bdo you remember my\b",
    r"\bdo you remember when i\b",
    r"\bdid i\b",
    r"\bhave i\b",
    r"\bwhen did i\b",
    r"\bwhere did i\b",
    r"\bwhat did i\b",
    r"\bwhy did i\b",
    r"\bwho did i\b",
    r"\bwhat was i\b",
    r"\bwhat am i\b",
    r"\bwhere i first met\b",
    r"\bfirst met\b",
]


def is_personal_question(question):
    """
    Check if a question is about Aditya's personal facts.
    Uses word-boundary regex so "my" doesn't match inside "mystery".
    """
    question_lower = question.lower().strip()
    
    for pattern in PERSONAL_PATTERNS:
        if re.search(pattern, question_lower):
            return True
    
    return False


def extract_memory_key(question):
    """
    Extract the specific memory key from a personal question.
    Example: "what is my favorite movie" → "favourite_movie"
             "what is my school" → "my_school"
             "what is my name" → "name"
    """
    question = question.lower().strip()
    
    # Edge cases first
    if question in ["who am i", "tell me about myself", "tell me about me", "what do you know about me"]:
        return "name"
    
    # Remove common question starters
    patterns_to_remove = [
        r"^what is my ",
        r"^what are my ",
        r"^what were my ",
        r"^where is my ",
        r"^when is my ",
        r"^who is my ",
        r"^do you remember my ",
        r"^do you remember ",
        r"^did i ",
        r"^have i ",
        r"^when did i ",
        r"^where did i ",
        r"^what did i ",
        r"^why did i ",
        r"^who did i ",
        r"^what was i ",
        r"^what am i ",
        r"^about me ",
        r"^for me ",
    ]
    
    key = question
    for pattern in patterns_to_remove:
        key = re.sub(pattern, "", key, count=1)
    
    # Clean up
    key = key.strip().rstrip("?").strip()
    key = key.replace(" ", "_")
    
    # Key aliases — map common variations to stored keys
    key_mapping = {
        "favorite_movie": "favourite_movie",
        "favourite_movie": "favourite_movie",
        "favorite_color": "favorite_color",
        "favourite_color": "favorite_color",
        "favorite_food": "favorite_food",
        "favourite_food": "favorite_food",
        "name": "name",
        "age": "age",
        "hobby": "hobby",
        "project": "project",
        "goal": "goal",
        "school": "my_school",
        "city": "my_city",
        "country": "my_country",
        "pet": "my_pet",
        "birthday": "my_birthday",
        "location": "my_location",
        "timezone": "my_timezone",
    }
    
    if key in key_mapping:
        return key_mapping[key]
    
    return key


def has_verified_memory(question):
    """
    Check if the SPECIFIC memory key exists, not just any memory.
    """
    # Edge case: "who am i" should check for "name"
    if question.strip().lower() in ["who am i", "tell me about myself", "tell me about me", "what do you know about me"]:
        all_memory = get_all_memory()
        return "name" in all_memory
    
    # If not personal, no grounding needed
    if not is_personal_question(question):
        return True
    
    # Extract the specific key
    key = extract_memory_key(question)
    
    # Get all memory
    all_memory = get_all_memory()
    
    # Check exact match
    if key in all_memory:
        return True
    
    # Also check substring match (e.g., "movie" in "favourite_movie")
    for memory_key in all_memory.keys():
        if key in memory_key or memory_key in key:
            return True
    
    return False


def validate_personal_question(question):
    """
    Returns True if the question can be answered (has memory or isn't personal).
    """
    if not is_personal_question(question):
        return True
    
    if has_verified_memory(question):
        return True
    
    return False


def grounding_response(question):
    """
    Returns:
    - None if grounding passes (question is allowed)
    - "I don't remember that yet, bro." if grounding blocks it
    """
    if not validate_personal_question(question):
        return "I don't remember that yet, bro."
    
    return None