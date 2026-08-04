from datetime import datetime

session_start = datetime.now()
command_count = 0


def add_command():
    global command_count
    command_count += 1


def get_command_count():
    return command_count


def get_session_minutes():
    return int((datetime.now() - session_start).total_seconds() // 60)