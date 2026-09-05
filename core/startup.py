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
import keyboard


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

    last_seen = get_last_seen()
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
            dt = datetime.fromisoformat(last_seen)
            formatted_last_seen = dt.strftime("%A, %d %B %Y at %I:%M %p")
            print(f"Last seen: {formatted_last_seen}")

    else:
        print("\nHello! I'm R1.")

    print()

    update_last_seen()

    while True:
        command = input(">>> ")

        if not command.strip():
            continue

        # If user types "mic", switch to voice input for this command
        if command.lower() == "mic":
            print("\n🎙️ Voice mode activated... Speak now")
            from modules.voice.listen import listen_to_mic
            from modules.modes.mode import get_mode_config
            voice_command = listen_to_mic(5)
            if not voice_command:
                print("No speech detected. Please type your command.")
                continue
            command = voice_command

        if command.lower() == "exit":
            print("Goodbye!")
            return  # This now exits the start() function properly

        add_message(command)
        process_command(command)

    while True:
        # Check if we're in idle mode — only respond when spoken to
        mode = get_mode_config()
        if mode["name"] == "Idle Mode":
            # No proactive messages — wait for input
            pass
        
        command = input(">>> ")

        if not command.strip():
            continue

        # If user types "mic", switch to voice input for this command
        if command.lower() == "mic":
            print("\n🎙️ Voice mode activated... Speak now")
            from modules.voice.listen import listen_to_mic
            voice_command = listen_to_mic(5)
            if not voice_command:
                print("No speech detected. Please type your command.")
                continue
            command = voice_command

        if command.lower() == "exit":
            print("Goodbye!")
            return

        add_message(command)
        process_command(command)