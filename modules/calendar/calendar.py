from modules.calendar.date_parser import extract_date

def find_calendar_event_in_text(text, country="India"):

    date = extract_date(text)

    if not date:
        return None

    return get_special_date(date, country)
# ==========================
# RAF Calendar Knowledge
# ==========================

from datetime import datetime


FIXED_DATES = {
    "01-26": {
        "name": "Republic Day",
        "country": "India"
    },

    "08-15": {
        "name": "Independence Day",
        "country": "India"
    },

    "10-02": {
        "name": "Gandhi Jayanti",
        "country": "India"
    }
}


def get_special_date(date, country="India"):

    month_day = date.strftime("%m-%d")

    event = FIXED_DATES.get(month_day)

    if not event:
        return None

    if event["country"] != country:
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