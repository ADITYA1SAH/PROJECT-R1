from modules.memory.memory import (
    recall,
    find_relevant_memories
)


def handle_recall(recall_result):

    # Try exact memory lookup first
    value = recall(recall_result["key"])

    if value:
        print(f"Your {recall_result['question']} is {value}.")
        return

    # If exact lookup fails, use relevant-memory search
    memories = find_relevant_memories(
        recall_result["question"]
    )

    if memories:

        # Take the highest-ranked memory
        key, value = next(iter(memories.items()))

        print(f"Your {key.replace('_', ' ')} is {value}.")
        return

    print("I don't remember that yet.")