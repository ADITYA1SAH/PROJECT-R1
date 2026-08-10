from modules.context.conversation import (
    get_topic,
    clear_topic
)
from modules.memory.experience import add_experience
from modules.memory.memory import recall
from modules.memory.experience import add_named_experience
COMMAND_PREFIXES = (
    "show ",
    "find ",
    "remember ",
    "forget ",
    "be ",
    "who am i",
    "what is",
    "what did",
    "owner",
    "friend",
    "guest"
)
def is_command(text):
    text = text.lower().strip()

    for prefix in COMMAND_PREFIXES:
        if text.startswith(prefix):
            return True

    return False


def handle_conversation(command):

    topic = get_topic()

    if topic == "happy_story":

        print("That sounds really nice.")
        print("I'm glad you shared that with me.")
        name = recall("name")

        if not name:
            name = "User"

        if not is_command(command):
            add_named_experience(name, command)
        
        clear_topic()

        return True
    
        
    if topic == "sad_story":

        print("Thanks for telling me.")
        print("I hope things improve soon.")
        if not is_command(command):
            if not is_command(command):
                add_experience(command)
        clear_topic()

        return True

    if topic == "angry_story":

        print("I can understand why that would be frustrating.")
        add_experience(command)
        clear_topic()

        return True

    return False