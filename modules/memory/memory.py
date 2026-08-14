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

def find_relevant_memories(question):

    memories = get_all_memory()

    question = question.lower()

    aliases = {
        "project": [
            "project",
            "build",
            "building",
            "creating",
            "work",
            "working"
        ],

        "goal": [
            "goal",
            "dream",
            "purpose",
            "mission",
            "ambition",
            "objective"
        ],

        "hobby": [
            "hobby",
            "interest",
            "passion",
            "like",
            "enjoy"
        ],

        "favorite_food": [
            "food",
            "eat",
            "meal",
            "favorite food",
            "favourite food"
        ],

        "favourite_movie": [
            "movie",
            "film",
            "favorite movie",
            "favourite movie"
        ]
    }

    relevant = {}

    for key, value in memories.items():

        score = 0

        words = key.replace("_", " ").split()

        for word in words:

            if word in question:
                score += 2

        if key in aliases:

            for alias in aliases[key]:

                if alias in question:
                    score += 3

        if score > 0:
            relevant[key] = (value, score)

    # Sort by score (highest first)
    sorted_memories = sorted(
        relevant.items(),
        key=lambda item: item[1][1],
        reverse=True
    )

    # Keep only top 5 memories
    result = {}

    for key, (value, score) in sorted_memories[:5]:
        result[key] = value

    return result