from modules.memory.memory import find_relevant_memories, get_all_memory
import re

PERSONAL_PATTERNS = [
    "my ",
    "about me",
    "for me",
    "do you remember",
    "did i ",
    "have i ",
    "when did i ",
    "where did i ",
    "what did i ",
    "why did i ",
    "who did i ",
    "what was i ",
    "what am i ",
    "what is my ",
    "what are my ",
    "what were my ",
    "who am i",
    "tell me about myself",
    "tell me about me",
    "what do you know about me",
]

def is_personal_question(question):
    question = question.lower().strip()

    for pattern in PERSONAL_PATTERNS:
        if pattern in question:
            return True

    return False

def extract_memory_key(question):
    """
    Extract the specific memory key from a personal question.
    Example: "what is my favorite movie" → "favorite_movie"
             "what is my school" → "school"
             "what is my name" → "name"
    """
    question = question.lower().strip()
    
    # Remove common question starters
    patterns_to_remove = [
        r"^what is my ",
        r"^what are my ",
        r"^what were my ",
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
    
    # Remove trailing question marks, spaces, and common filler words
    key = key.strip().rstrip("?")
    
    # Replace spaces with underscores for key format
    key = key.replace(" ", "_")
    
    # Handle special cases
    key_mapping = {
        "favorite_movie": "favourite_movie",
        "favourite_movie": "favourite_movie",
        "favorite_color": "favorite_color",
        "favourite_color": "favorite_color",
        "favorite_food": "favorite_food",
        "favourite_food": "favorite_food",
        "my_name": "name",
        "name": "name",
        "age": "age",
        "hobby": "hobby",
        "robotics": "hobby",  # if they ask about robotics, map to hobby
        "project_r1": "project",
        "project": "project",
        "goal": "goal",
    }
    
    if key in key_mapping:
        return key_mapping[key]
    
        # Handle "who am i" and "tell me about myself" edge cases

    if question in ["who am i", "tell me about myself", "tell me about me", "what do you know about me"]:
        return "name"
    return key

def has_verified_memory(question):
        # Edge case: "who am i" should check for "name"
    if question.strip().lower() in ["who am i", "tell me about myself", "tell me about me", "what do you know about me"]:
        all_memory = get_all_memory()
        return "name" in all_memory
    """
    Check if the SPECIFIC memory key exists, not just any memory.
    """
    # First check if it's personal at all
    if not is_personal_question(question):
        return True  # Not personal, so no grounding needed
    
    # Extract the specific key
    key = extract_memory_key(question)
    
    # Get all memory
    all_memory = get_all_memory()
    
    # Check if this specific key exists
    if key in all_memory:
        return True
    
    # Also check if the key appears as a substring in any memory key
    # (e.g., "movie" in "favourite_movie")
    for memory_key in all_memory.keys():
        if key in memory_key or memory_key in key:
            return True
    
    return False

def validate_personal_question(question):
    if not is_personal_question(question):
        return True

    if has_verified_memory(question):
        return True

    return False

def grounding_response(question):
    if not validate_personal_question(question):
        return "I don't remember that yet, bro."

    return None