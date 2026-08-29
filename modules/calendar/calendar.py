from modules.calendar.date_parser import extract_date

def find_calendar_event_in_text(text, country="India"):

    date = extract_date(text)

    if not date:
        return None

    return get_special_date(date, country)

def is_calendar_question(text):
    """
    Detect if a question is asking about calendar/date-related information.
    """
    text = text.lower()
    calendar_keywords = [
        "holiday", "festival", "celebration", "special day",
        "what day", "what date", "when is", "what's on",
        "is there any", "any holiday", "any festival",
        "today", "tomorrow", "yesterday", "this week",
        "upcoming", "coming up", "calendar", "date"
    ]
    return any(keyword in text for keyword in calendar_keywords)

# ==========================
# RAF Calendar Knowledge
# ==========================

from datetime import datetime


FIXED_DATES = {
    # National Holidays (India)
    "01-26": {"name": "Republic Day", "country": "India", "type": "national"},
    "08-15": {"name": "Independence Day", "country": "India", "type": "national"},
    "10-02": {"name": "Gandhi Jayanti", "country": "India", "type": "national"},
    "05-01": {"name": "International Workers' Day", "country": "India", "type": "national"},
    
    # Global Festivals
    "01-01": {"name": "New Year's Day", "country": "Global", "type": "festival"},
    "02-14": {"name": "Valentine's Day", "country": "Global", "type": "festival"},
    "03-08": {"name": "International Women's Day", "country": "Global", "type": "festival"},
    "04-01": {"name": "April Fools' Day", "country": "Global", "type": "festival"},
    "10-31": {"name": "Halloween", "country": "Global", "type": "festival"},
    "12-25": {"name": "Christmas Day", "country": "Global", "type": "festival"},
    "12-31": {"name": "New Year's Eve", "country": "Global", "type": "festival"},
}


def get_special_date(date, country="India"):
    month_day = date.strftime("%m-%d")
    event = FIXED_DATES.get(month_day)
    if not event:
        return None
    if event["country"] != country and event["country"] != "Global":
        return None
    return event


def is_special_date(date, country="India"):

    return get_special_date(date, country) is not None


def get_calendar_event(date, country="India"):

    event = get_special_date(date, country)

    if not event:
        return None

    return f"{event['name']} ({event['country']})"


def get_event_for_date(year, month, day, country="India"):

    date = datetime(year, month, day)

    return get_special_date(date, country)


# ==========================
# Test
# ==========================

if __name__ == "__main__":

    test_date = datetime(2026, 8, 15)

    print("Special date:")
    print(get_special_date(test_date))

    print("\nCalendar event:")
    print(get_calendar_event(test_date))

    print("\nEvent for date:")
    print(get_event_for_date(2026, 8, 15))

if __name__ == "__main__":

    test_question = "What is special about August 15?"

    result = find_calendar_event_in_text(test_question)

    print("Question:")
    print(test_question)

    print("\nCalendar result:")
    print(result)