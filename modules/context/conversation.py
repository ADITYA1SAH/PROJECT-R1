CURRENT_TOPIC = None


def set_topic(topic):
    global CURRENT_TOPIC
    CURRENT_TOPIC = topic


def get_topic():
    return CURRENT_TOPIC


def clear_topic():
    global CURRENT_TOPIC
    CURRENT_TOPIC = None

conversation_history = []


def add_message(message):

    conversation_history.append(message)

    # Keep only the last 10 messages
    if len(conversation_history) > 10:
        conversation_history.pop(0)


def get_last_message():

    if len(conversation_history) >= 2:
        return conversation_history[-2]

    return ""


def get_conversation_history():

    return conversation_history