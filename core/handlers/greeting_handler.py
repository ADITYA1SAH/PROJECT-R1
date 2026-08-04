from modules.personality.responses import random_greeting


def handle_greeting(command):

    greetings = [

        "hi",

        "hello",

        "hey"

    ]

    if command.lower() in greetings:

        print(random_greeting())

        return True

    return False