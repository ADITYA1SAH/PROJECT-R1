import json
import os

MEMORY_FILE = "database/memory.json"

def normalize_key(key):
    return key.strip().lower().replace(" ", "_")

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as file:
        return json.load(file)


def save_memory(data):
    with open(MEMORY_FILE, "w") as file:
        json.dump(data, file, indent=4)


def remember(key, value):
    key = normalize_key(key)

    memory = load_memory()
    memory[key] = value
    save_memory(memory)

def recall(key):
    key = normalize_key(key)

    memory = load_memory()
    return memory.get(key)

def forget(key):
    key = normalize_key(key)

    memory = load_memory()

    if key in memory:
        del memory[key]
        save_memory(memory)
        return True

    return False


def get_all_memory():
    return load_memory()