from modules.context.conversation import get_last_message


def handle_last_message():

    last = get_last_message()

    if last:
        print(f"You just said: '{last}'")
    else:
        print("I don't remember your last message.")