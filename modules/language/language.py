import re


def get_memory_statement(command):
    # Pattern 1: "my X is Y" (standard)
    match = re.match(r"my (.+) is (.+)", command)
    if match:
        key = match.group(1).strip().replace(" ", "_")
        value = match.group(2).strip()
        
        # Sanity check: if value contains " is " again, it's probably a mangled statement
        # Take only the first part before the second " is "
        if " is " in value.lower():
            value = value.split(" is ")[0].strip()
        
        # Also reject if value is too long (over 100 chars)
        if len(value) > 100:
            return None
        
        return {
            "intent": "remember",
            "key": key,
            "value": value
        }
    
    # Pattern 2: "my friend X is Y" — capture as "friend_X"
    match = re.match(r"my friend (\w+) is (.+)", command)
    if match:
        friend_name = match.group(1).strip()
        value = match.group(2).strip()
        return {
            "intent": "remember",
            "key": f"friend_{friend_name.lower()}",
            "value": value
        }
    
    # Pattern 3: "my friend X loves Y" — capture as "friend_X_loves"
    match = re.match(r"my friend (\w+) loves? (.+)", command)
    if match:
        friend_name = match.group(1).strip()
        what = match.group(2).strip()
        return {
            "intent": "remember",
            "key": f"friend_{friend_name.lower()}",
            "value": f"loves {what}"
        }
    
    return None


def get_remember_command(command):
    if command.startswith("remember "):
        data = command.replace("remember ", "", 1).strip()
        if "=" in data:
            key, value = data.split("=", 1)
            return {
                "intent": "remember",
                "key": key.strip().replace(" ", "_"),
                "value": value.strip()
            }
        match = re.match(r"my (.+) is (.+)", data)
        if match:
            return {
                "intent": "remember",
                "key": match.group(1).strip().replace(" ", "_"),
                "value": match.group(2).strip()
            }
    return None


def get_recall_command(command):
    command = command.lower().strip()
    ALIAS_MAP = {
        "country": "my_country",
        "school": "my_school",
        "city": "my_city",
        "pet": "my_pet",
        "birthday": "my_birthday",
        "food": "favorite_food",
        "movie": "favourite_movie",
        "color": "favorite_color",
    }
    personal_prefixes = (
        "what is my ",
        "what's my ",
        "what was my ",
        "what are my ",
        "what were my ",
    )
    if not command.startswith(personal_prefixes):
        return None
    if command.startswith("what is my "):
        question = command.replace("what is my ", "", 1).strip()
    elif command.startswith("what's my "):
        question = command.replace("what's my ", "", 1).strip()
    elif command.startswith("what was my "):
        question = command.replace("what was my ", "", 1).strip()
    elif command.startswith("what are my "):
        question = command.replace("what are my ", "", 1).strip()
    else:
        question = command.replace("what were my ", "", 1).strip()
    key = question.replace(" ", "_")
    if key in ALIAS_MAP:
        key = ALIAS_MAP[key]
    elif not key.startswith("my_"):
        key = f"my_{key}"
    return {
        "intent": "recall",
        "key": key,
        "question": question
    }


def get_personal_lookup(command):
    """
    Extract the key from personal questions.
    Handles: "what is my X", "where do i X", "when is my X", etc.
    """
    command = command.lower().strip()
    
    # Special cases first
    special_cases = {
        "where do i live": "my_location",
        "where am i": "my_location",
        "where do i stay": "my_location",
        "when is my birthday": "my_birthday",
        "how old am i": "age",
        "do i have a pet": "my_pet",
        "do i have a pet?": "my_pet",
        "who am i": "name",
        "what is my name": "name",
    }
    
    if command in special_cases:
        return special_cases[command]
    
    # Standard prefix patterns (including "do you remember my X")
    prefixes = [
        "what is my ", "what's my ", "where is my ", "where's my ",
        "when is my ", "when's my ", "who is my ", "do i have a ",
        "do you remember my ", "do you remember ",
        "tell me about my ", "tell me about ",
    ]
    
    for prefix in prefixes:
        if command.startswith(prefix):
            key = command.replace(prefix, "").strip()
            key = re.sub(r'[^\w\s]', '', key)
            key = key.replace(" ", "_")
            if not key.startswith("my_"):
                key = f"my_{key}"
            return key
    
    return None


def get_mood_command(command):
    command = command.lower().strip()
    if command == "how are you":
        return {"intent": "mood"}
    return None


def get_last_message_command(command):
    command = command.lower().strip()
    if command == "what did i just say":
        return {"intent": "last_message"}
    return None