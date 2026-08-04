def detect_emotion(command):

    command = command.lower()

    if any(word in command for word in ["happy", "great", "awesome", "yay"]):
        return "happy"

    if any(word in command for word in ["sad", "depressed", "unhappy"]):
        return "sad"

    if any(word in command for word in ["angry", "mad", "furious"]):
        return "angry"

    if any(word in command for word in ["love", "thanks", "thank you"]):
        return "kind"

    return "neutral"


def emotion_icon(emotion):

    icons = {
        "happy": "😊",
        "sad": "😔",
        "angry": "😠",
        "kind": "❤️",
        "neutral": "😐"
    }

    return icons.get(emotion, "😐")