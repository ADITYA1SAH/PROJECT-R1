from modules.context.conversation import (
    get_topic,
    clear_topic
)
from modules.memory.experience import add_experience
from modules.memory.memory import recall
from modules.memory.experience import add_named_experience


def handle_conversation(command):

    topic = get_topic()

    if topic == "happy_story":

        print("That sounds really nice.")
        print("I'm glad you shared that with me.")
        name = recall("name")

        if not name:
            name = "User"

        add_named_experience(name, command)
        
        clear_topic()

        return True
    
        
    if topic == "sad_story":

        print("Thanks for telling me.")
        print("I hope things improve soon.")
        add_experience(command)
        clear_topic()

        return True

    if topic == "angry_story":

        print("I can understand why that would be frustrating.")
        add_experience(command)
        clear_topic()

        return True

    return False