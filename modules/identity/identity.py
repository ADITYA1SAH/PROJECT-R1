CURRENT_USER = "owner"


def get_identity():
    return CURRENT_USER


def set_identity(identity):
    global CURRENT_USER
    CURRENT_USER = identity


def is_owner():
    return CURRENT_USER == "owner"


def is_friend():
    return CURRENT_USER == "friend"


def is_guest():
    return CURRENT_USER == "guest"