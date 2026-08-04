from modules.memory.memory import remember


def handle_remember(data):

    remember(
        data["key"],
        data["value"]
    )

    print(
        f"I'll remember that {data['key'].replace('_',' ')} is '{data['value']}'."
    )