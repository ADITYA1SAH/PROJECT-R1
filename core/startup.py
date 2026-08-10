from datetime import datetime
from config import APP_NAME, VERSION, SHOW_BANNER, BANNER
from modules.memory.memory import recall
from core.brain import process_command
from modules.session.last_seen import (
    update_last_seen,
    get_last_seen
)
from modules.personality.responses import random_welcome
from modules.memory.experience import load_experiences
from modules.memory.daily_memory import get_today
from modules.memory.daily_memory import memory_count
from modules.context.conversation import add_message


def get_greeting():
    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 21:
        return "Good Evening"
    else:
        return "Good Night"


def start():
    if SHOW_BANNER:
        print(BANNER)

    last_seen = get_last_seen()    # ← INSERT HERE
    name = recall("name")

    load_experiences()
    
    if name:
        print(f"\n{get_greeting()}, {name}!")
        print(random_welcome())

        today = get_today()

        if today:

            count = len(today)

            if count == 1:
                print("You created 1 memory today.")

            else:
                print(f"You created {count} memories today.")

        print(f"Total memories: {memory_count()}")

        if last_seen:
            print(f"Last seen: {last_seen}")

    else:
        print("\nHello! I'm R1.")

    print()

    update_last_seen()  # Update the last seen timestamp

    while True:

        command = input(">>> ")

        if not command.strip():
            continue

        if command.lower() == "exit":
            print("Goodbye!")
            break

        add_message(command)      # <-- Add this line

        process_command(command)