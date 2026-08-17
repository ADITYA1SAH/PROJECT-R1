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

        # Format:
        # remember key = value

        if "=" in data:

            key, value = data.split("=", 1)

            return {
                "intent": "remember",
                "key": key.strip().replace(" ", "_"),
                "value": value.strip()
            }

        # Format:
        # remember my project is PROJECT R1

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

    # Only treat questions explicitly asking about
    # Aditya's personal information as memory recall.

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

    return {
        "intent": "recall",
        "key": question.replace(" ", "_"),
        "question": question
    }


def get_mood_command(command):

    command = command.lower().strip()

    if command == "how are you":

        return {
            "intent": "mood"
        }

    return None


def get_last_message_command(command):

    command = command.lower().strip()

    if command == "what did i just say":

        return {
            "intent": "last_message"
        }

    return None