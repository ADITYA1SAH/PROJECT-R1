from modules.session.session import (
    get_command_count,
    get_session_minutes
)

def handle_show_session():

    print("\n----- Session -----")
    print(f"Commands: {get_command_count()}")
    print(f"Time: {get_session_minutes()} minute(s)")