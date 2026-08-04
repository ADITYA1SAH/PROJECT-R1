from datetime import datetime
from modules.memory.memory import remember, recall


def update_last_seen():
    now = datetime.now().isoformat()
    remember("last_seen", now)


def get_last_seen():
    return recall("last_seen")