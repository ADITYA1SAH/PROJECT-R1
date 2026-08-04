from modules.identity.identity import is_owner


def require_owner():

    if is_owner():
        return True

    print("Sorry, only the owner can use this command.")
    return False