from modules.memory.memory import recall
from modules.memory.experience import get_recent
from modules.memory.daily_memory import get_today
from modules.memory.summary import get_daily_summary


def get_memory_context():

    return {

    "owner": recall("name") or "User",

    "today": get_today(),

    "summary": get_daily_summary(),

    "recent": get_recent()

}