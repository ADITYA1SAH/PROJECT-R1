import random

# Emotion responses (used when the user expresses an emotion)

RESPONSES = {
    "happy": [
        "😊 I'm happy to hear that!",
        "😊 That's awesome!",
        "😊 Glad you're feeling good!"
    ],

    "sad": [
        "😔 I'm sorry you're feeling that way.",
        "😔 I hope things get better.",
        "😔 I'm here if you want to talk."
    ],

    "angry": [
        "😠 That sounds frustrating.",
        "😠 I understand why you'd feel that way.",
        "😠 Let's see if we can fix it."
    ],

    "kind": [
        "❤️ Thank you! That means a lot.",
        "❤️ I appreciate that.",
        "❤️ That's really kind of you."
    ],

    "neutral": [
        "😐"
    ]
}


# Mood responses (used when the user asks 'how are you?')

MOOD_RESPONSES = {

    "happy": [
        "I'm doing great today!",
        "I'm feeling pretty good.",
        "Today's been a good day.",
        "I'm in a great mood."
    ],

    "sad": [
        "I've been feeling a little down.",
        "Not my best day, honestly.",
        "I'm feeling a bit low today."
    ],

    "angry": [
        "I'm a little frustrated.",
        "I've had better days.",
        "I'm trying to stay calm."
    ],

    "kind": [
        "I'm doing well. Thanks for asking.",
        "Pretty good, actually.",
        "I'm doing alright."
    ],

    "neutral": [
        "I'm doing okay.",
        "I'm alright.",
        "Everything's going smoothly.",
        "Not bad."
    ]
}


def random_response(emotion):
    return random.choice(RESPONSES.get(emotion, RESPONSES["neutral"]))


def random_mood_response(emotion):
    return random.choice(
        MOOD_RESPONSES.get(
            emotion,
            MOOD_RESPONSES["neutral"]
        )
    )