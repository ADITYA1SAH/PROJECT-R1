from modules.memory.memory import remember, recall
saved = recall("current_emotion")

if saved:
    current_emotion = saved
else:
    current_emotion = "neutral"

def set_emotion(emotion):
    global current_emotion

    current_emotion = emotion

    remember("current_emotion", emotion)

def get_emotion():
    return current_emotion