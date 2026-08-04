from modules.identity.override import OVERRIDE_CODE
from modules.identity.identity import set_identity


def handle_override(command):

    if command.strip().upper() == OVERRIDE_CODE:

        set_identity("owner")

        print("Override accepted.")
        print("Owner access restored.")

        return True

    return False