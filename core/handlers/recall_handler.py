from modules.memory.memory import recall


def handle_recall(recall_result):

    value = recall(recall_result["key"])

    if value:
        print(f"Your {recall_result['question']} is {value}.")
    else:
        print("I don't remember that yet.")