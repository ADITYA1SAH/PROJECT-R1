"""
Permanent Memory for PROJECT R1
Like human long-term memory — NEVER deleted, NEVER replaced.
Stores: family, identity, life events, important people, core memories.
"""

import json
import os
from datetime import datetime

PERMANENT_FILE = "data/permanent_memory.json"

# Categories — like different types of human memory
CATEGORIES = [
    "family",
    "identity",
    "life_events",
    "people",
    "places",
    "values",
    "stories",
    "preferences",
    "goals",
]


def load_permanent():
    if not os.path.exists(PERMANENT_FILE):
        return []
    with open(PERMANENT_FILE, "r") as f:
        return json.load(f)


def save_permanent(data):
    os.makedirs("data", exist_ok=True)
    with open(PERMANENT_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_permanent(fact, category="general", context=""):
    """
    Add a permanent memory — NEVER deleted, NEVER replaced.
    """
    data = load_permanent()
    data.append({
        "id": len(data) + 1,
        "fact": fact,
        "category": category,
        "context": context,
        "timestamp": datetime.now().isoformat(),
        "archived": False
    })
    save_permanent(data)
    return True


def get_permanent(category=None):
    data = load_permanent()
    if category:
        return [m for m in data if m["category"] == category]
    return data


def get_family():
    return get_permanent("family")


def get_identity():
    return get_permanent("identity")


def search_permanent(keyword):
    data = load_permanent()
    keyword = keyword.lower()
    return [m for m in data if keyword in m["fact"].lower()]