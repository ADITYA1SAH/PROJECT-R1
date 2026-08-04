from modules.memory.memory import remember, recall


def set_last_message(message):
    remember("last_message", message)


def get_last_message():
    return recall("last_message")