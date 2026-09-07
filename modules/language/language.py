import re


def get_memory_statement(command):
    match = re.match(r"my (.+) is (.+)", command)
    if match:
        key = match.group(1).strip().replace(" ", "_")
        value = match.group(2).strip()
        return {
            "intent": "remember",
            "key": key,
            "value": value
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
    Extract the key from "what is my X" and return it.
    Example: "what is my country" → "my_country"
    """
    command = command.lower().strip()
    if not command.startswith(("what is my ", "what's my ", "where is my ", "when is my ", "do i have a ")):
        return None
    for prefix in ["what is my ", "what's my ", "where is my ", "when is my ", "do i have a "]:
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