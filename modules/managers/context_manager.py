from modules.managers.memory_manager import get_memory_context
from modules.emotion.state import get_emotion
from modules.context.conversation import get_conversation_history


def get_context():

    memory = get_memory_context()

    return {

        "owner": memory["owner"],

        "today": memory["today"],

        "summary": memory["summary"],

        "recent": memory["recent"],

        "emotion": get_emotion(),

        "conversation": get_conversation_history()

    }