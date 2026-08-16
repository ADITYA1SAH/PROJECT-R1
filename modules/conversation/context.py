from modules.time.time import get_current_time


CURRENT_TOPIC = None

conversation_history = []


def set_topic(topic):

    global CURRENT_TOPIC

    CURRENT_TOPIC = topic


def get_topic():

    return CURRENT_TOPIC


def clear_topic():

    global CURRENT_TOPIC

    CURRENT_TOPIC = None


def add_message(role, content):

    current_time = get_current_time()

    conversation_history.append({
        "role": role,
        "content": content,
        "timestamp": current_time["timestamp"]
    })

    # Keep only the last 50 messages
    if len(conversation_history) > 50:
        del conversation_history[:-50]


def get_last_message():

    if len(conversation_history) >= 2:
        return conversation_history[-2]

    return ""


def get_conversation_history():

    return conversation_history


def get_recent_history(limit=10):

    return conversation_history[-limit:]


def clear_history():

    conversation_history.clear()