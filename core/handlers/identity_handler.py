from modules.identity.identity import (
    set_identity,
    get_identity
)


def handle_identity(command):

    if command == "be owner":
        set_identity("owner")
        print("Identity changed to Owner.")
        return True

    if command == "be friend":
        set_identity("friend")
        print("Identity changed to Friend.")
        return True

    if command == "be guest":
        set_identity("guest")
        print("Identity changed to Guest.")
        return True

    if command == "who am i":
        print(f"Current identity: {get_identity()}")
        return True

    return False