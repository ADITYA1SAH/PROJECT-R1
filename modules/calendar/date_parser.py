import re
from datetime import datetime


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12
}


def extract_date(text, year=None):

    if year is None:
        year = datetime.now().year

    text = text.lower()

    pattern = (
        r"\b("
        + "|".join(MONTHS.keys())
        + r")\s+(\d{1,2})(?:st|nd|rd|th)?"
        r"(?:,?\s+(\d{4}))?\b"
    )

    match = re.search(pattern, text)

    if not match:
        return None

    month_name = match.group(1)
    day = int(match.group(2))

    if match.group(3):
        year = int(match.group(3))

    month = MONTHS[month_name]

    try:
        return datetime(year, month, day)

    except ValueError:
        return None

if __name__ == "__main__":

    tests = [
        "What is special about August 15?",
        "What happened on August 15th?",
        "What is special about August 15, 2026?",
        "Tell me about December 25"
    ]

    for text in tests:

        result = extract_date(text)

        print(text)
        print("→", result)
        print()