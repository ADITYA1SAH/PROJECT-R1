from modules.memory.experience import get_recent


def get_relevant_memories(query):

    query = query.lower()

    results = []

    for memory in get_recent():

        if query in memory.lower():

            results.append(memory)

    return results