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

        data = command.replace("remember ", "", 1)

        if "=" in data:

            key, value = data.split("=", 1)

            return {
                "intent": "remember",
                "key": key.strip(),
                "value": value.strip()
            }

    return None
def get_recall_command(command):

    if command.startswith("what is "):

        question = command.replace("what is ", "", 1).strip()

        question = question.replace("my ", "")

        return {
            "intent": "recall",
            "key": question.replace(" ", "_"),
            "question": question
        }

    return None

def get_mood_command(command):

    if command == "how are you":
        return {
            "intent": "mood"
        }

    return None
def get_last_message_command(command):

    if command == "what did i just say":
        return {
            "intent": "last_message"
        }

    return None