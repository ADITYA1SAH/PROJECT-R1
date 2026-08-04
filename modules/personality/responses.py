import random

UNKNOWN_RESPONSES = [

    "Hmm... I haven't learned that yet.",

    "That's new to me.",

    "Interesting... tell me more.",

    "I'm not sure what you mean yet.",

    "I haven't figured that one out yet.",

    "Could you explain it another way?",

    "I'm still learning every day."

]
import random

GREETINGS = [

    "Hey!",

    "Hi!",

    "Hello!",

    "Hey Aditya!",

    "Good to see you."

]
WELCOME_RESPONSES = {

    "morning": [

        "Hope you slept well.",
        "Ready to start the day?",
        "Good to see you this morning.",
        "Let's make today productive."

    ],

    "afternoon": [

        "Welcome back.",
        "Hope your day's going well.",
        "Ready to continue?",
        "Let's get back to work."

    ],

    "evening": [

        "It's good to see you again.",
        "Ready to continue where we left off?",
        "Let's build something today.",
        "Glad you're back."

    ],

    "night": [

        "Burning the midnight oil again?",
        "You're up late again.",
        "Another late-night coding session?",
        "Let's make some progress before sleep."
    ]
}


def random_greeting():

    return random.choice(GREETINGS)

from datetime import datetime
import random


def random_welcome():

    hour = datetime.now().hour

    if 5 <= hour < 12:
        period = "morning"

    elif 12 <= hour < 17:
        period = "afternoon"

    elif 17 <= hour < 21:
        period = "evening"

    else:
        period = "night"

    return random.choice(WELCOME_RESPONSES[period])

def unknown_response():

    return random.choice(UNKNOWN_RESPONSES)

FOLLOW_UP = {

    "happy": [
        "What happened?",
        "Did something good happen today?",
        "Want to tell me about it?"
    ],

    "sad": [
        "Want to talk about it?",
        "Anything I can help with?",
        "What happened?"
    ],

    "angry": [
        "What happened?",
        "Want to vent a little?",
        "Who annoyed you?"
    ],

    "kind": [
        "😊",
        "You're always welcome.",
        "That made my day."
    ]
}

def random_follow_up(emotion):

    if emotion not in FOLLOW_UP:
        return ""

    return random.choice(FOLLOW_UP[emotion])