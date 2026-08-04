from modules.memory.memory import forget


def handle_forget(command):

    key = command.replace("forget ", "", 1).strip()
    key = key.replace(" ", "_")

    if forget(key):
        print(f"I forgot {key}.")
    else:
        print(f"I don't remember {key}.")