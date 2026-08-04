import json
import os
from modules.memory.daily_memory import add_today

FILE = "memory_experience.json"

EXPERIENCES = []


def load_experiences():
    global EXPERIENCES

    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            EXPERIENCES = json.load(f)


def save_experiences():

    with open(FILE, "w") as f:
        json.dump(EXPERIENCES, f, indent=4)


def add_experience(text):

    EXPERIENCES.append(text)

    add_today(text)

    save_experiences()

def get_recent(count=5):

    return EXPERIENCES[-count:]

def add_named_experience(name, text):

    add_experience(f"{name}: {text}")

def search_experiences(keyword):

    keyword = keyword.lower()

    results = []

    for exp in EXPERIENCES:

        if keyword in exp.lower():

            results.append(exp)

    return results