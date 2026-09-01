from modules.emotion.state import get_emotion
def handle_mood():
    current = get_emotion()
    from modules.emotion.responses import random_mood_response
    response = random_mood_response(current)
    print(response)
    return response