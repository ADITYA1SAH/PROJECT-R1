from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


TIMEZONE = "Asia/Kolkata"


def get_current_time():

    now = datetime.now(ZoneInfo(TIMEZONE))

    return {
        "timestamp": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day": now.strftime("%A"),
        "timezone": TIMEZONE,
        "formatted": now.strftime("%A, %d %B %Y at %I:%M:%S %p")
    }

def get_calendar_context():

    current = get_current_time()

    current_date = datetime.fromisoformat(
        current["timestamp"]
    )

    yesterday = current_date - timedelta(days=1)
    tomorrow = current_date + timedelta(days=1)

    return {
        "today": current["date"],
        "yesterday": yesterday.strftime("%Y-%m-%d"),
        "tomorrow": tomorrow.strftime("%Y-%m-%d"),
        "day": current["day"],
        "timezone": current["timezone"]
    }


def get_relative_time(timestamp):

    current = datetime.now(ZoneInfo(TIMEZONE))
    message_time = datetime.fromisoformat(timestamp)

    difference = current - message_time
    seconds = int(difference.total_seconds())

    if seconds < 60:
        return "just now"

    minutes = seconds // 60

    if minutes == 1:
        return "1 minute ago"

    if minutes < 60:
        return f"{minutes} minutes ago"

    hours = minutes // 60

    if hours == 1:
        return "1 hour ago"

    if hours < 24:
        return f"{hours} hours ago"

    days = hours // 24

    if days == 1:
        return "yesterday"

    return f"{days} days ago"


if __name__ == "__main__":

    current = get_current_time()

    print(current)

    print(get_relative_time(current["timestamp"]))

    print(get_calendar_context())