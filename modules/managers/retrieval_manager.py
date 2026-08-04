from modules.memory.relevance import get_relevant_memories


def retrieve(query):

    return {

        "relevant": get_relevant_memories(query)

    }