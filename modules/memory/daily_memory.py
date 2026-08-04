import json
import os
from datetime import date

FILE = "daily_memory.json"


def load_daily():

    if os.path.exists(FILE):

        with open(FILE, "r") as f:

            return json.load(f)

    return {}


def save_daily(data):

    with open(FILE, "w") as f:

        json.dump(data, f, indent=4)


def add_today(entry):

    data = load_daily()

    today = str(date.today())

    if today not in data:

        data[today] = []

    data[today].append(entry)

    save_daily(data)


def get_today():

    data = load_daily()

    return data.get(str(date.today()), [])

from datetime import date, timedelta


def get_yesterday():

    data = load_daily()

    yesterday = str(date.today() - timedelta(days=1))

    return data.get(yesterday, [])

def memory_count():

    data = load_daily()

    total = 0

    for memories in data.values():

        total += len(memories)

    return total

def search_daily(keyword):

    keyword = keyword.lower()

    data = load_daily()

    results = []

    for day, memories in data.items():

        for memory in memories:

            if keyword in memory.lower():

                results.append((day, memory))

    return results