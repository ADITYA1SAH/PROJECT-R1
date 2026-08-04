from modules.emotion.responses import random_response
from modules.emotion.emotion import emotion_icon
from modules.personality.responses import random_follow_up
from modules.context.conversation import set_topic

def handle_emotion(emotion):

    print(f"{emotion_icon(emotion)} [{emotion}]")

    print(random_response(emotion))

    follow = random_follow_up(emotion)
    if emotion == "happy":
        set_topic("happy_story")

    elif emotion == "sad":
        set_topic("sad_story")

    elif emotion == "angry":
        set_topic("angry_story")

    if follow:
        print(follow)