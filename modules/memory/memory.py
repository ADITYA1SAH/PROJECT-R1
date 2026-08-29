import json
import os
from difflib import SequenceMatcher
import re

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


def remember(key, value, confidence=1.0):
    key = normalize_key(key)
    memory = load_memory()
    memory[key] = {
        "value": value,
        "confidence": confidence
    }
    save_memory(memory)

def recall(key):
    key = normalize_key(key)
    memory = load_memory()
    entry = memory.get(key)
    if isinstance(entry, dict):
        return entry.get("value")
    return entry

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

    # Remove punctuation
    question = re.sub(r"[^\w\s]", "", question)

    # Normalize common question forms
    question = question.replace("whats", "what is")

    aliases = {
        "project": [
            "project",
            "projct",
            "build",
            "building",
            "creating",
            "work",
            "working"
        ],

        "goal": [
            "goal",
            "gole",
            "goals",
            "dream",
            "purpose",
            "mission",
            "ambition",
            "objective"
        ],

        "hobby": [
            "hobby",
            "hobbie",
            "hobbies",
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

    question_words = question.split()

    for key, value in memories.items():

        score = 0

        memory_words = key.replace("_", " ").split()

        # --------------------------------
        # Exact key-word matching
        # --------------------------------

        for memory_word in memory_words:

            if memory_word in question_words:
                score += 5

        # --------------------------------
        # Alias matching
        # --------------------------------

        if key in aliases:

            for alias in aliases[key]:

                alias_words = alias.split()

                # Single-word alias
                if len(alias_words) == 1:

                    if alias in question_words:
                        score += 10

                # Multi-word alias
                else:

                    if alias in question:
                        score += 10

        # --------------------------------
        # Fuzzy matching
        # --------------------------------

        for question_word in question_words:

            for memory_word in memory_words:

                similarity = SequenceMatcher(
                    None,
                    question_word,
                    memory_word
                ).ratio()

                if similarity >= 0.70:
                    score += 3

                elif (
                    len(question_word) <= 7
                    and len(memory_word) <= 7
                    and similarity >= 0.65
                ):
                    score += 3

        # --------------------------------
        # Save relevant memory
        # --------------------------------

        if score > 0:

            relevant[key] = (
                value,
                score
            )

    # --------------------------------
    # Sort by relevance
    # --------------------------------

    sorted_memories = sorted(
        relevant.items(),
        key=lambda item: item[1][1],
        reverse=True
    )

    # --------------------------------
    # Return top 5
    # --------------------------------

    result = {}

    for key, (value, score) in sorted_memories[:5]:

        result[key] = value

    return result