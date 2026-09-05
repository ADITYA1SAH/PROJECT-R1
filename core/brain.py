# =========================
# Memory
# =========================

from core.handlers.memory_handler import handle_remember
from core.handlers.recall_handler import handle_recall
from core.handlers.forget_handler import handle_forget
from core.handlers.show_memory_handler import handle_show_memory

# =========================
# Identity
# =========================

from core.handlers.identity_handler import handle_identity
from core.handlers.owner_handler import require_owner
from core.handlers.override_handler import handle_override

# =========================
# Conversation
# =========================

from core.handlers.greeting_handler import handle_greeting
from core.handlers.conversation_handler import handle_conversation
from core.handlers.last_message_handler import handle_last_message
from core.handlers.mood_handler import handle_mood
from core.handlers.unknown_handler import handle_unknown

# =========================
# Emotion
# =========================

from modules.emotion.emotion import detect_emotion
from modules.emotion.state import (
    set_emotion,
    get_emotion
)
from modules.emotion.reason import (
    set_reason,
    get_reason
)
from core.handlers.emotion_handler import handle_emotion

# =========================
# Session
# =========================

from modules.session.session import add_command
from core.handlers.session_handler import handle_show_session

# =========================
# Language Parser
# =========================

from modules.language.language import (
    get_memory_statement,
    get_remember_command,
    get_recall_command,
    get_mood_command,
    get_last_message_command
)

# =========================
# Other Imports
# =========================

from core.handlers.version_handler import handle_version
from config import USE_LLM
from config import VOICE_ENABLED
from modules.voice.voice import speak
from modules.llm.llm import generate_response
from modules.prompting.prompt_builder import build_prompt
from modules.conversation.context import (
    add_message,
    get_recent_history
)
from modules.internet.search import search
from modules.grounding.grounding import grounding_response
from modules.routing.intent_router import IntentRouter


def process_command(command):
    command = command.strip().lower()
    add_message("user", command)

    # =========================
    # Intelligence Router
    # =========================
    router = IntentRouter()
    route = router.route(command)

    # =========================
    # FAST COMMANDS — bypass LLM
    # =========================
    
    # Mode switching
    if command.startswith("mode "):
        from modules.modes.mode import set_mode, get_mode_config
        parts = command.split()
        if len(parts) == 2:
            mode_name = parts[1]
            if set_mode(mode_name):
                config = get_mode_config()
                print(f"✅ Mode switched to: {config['name']}")
                print(f"   {config['description']}")
                if VOICE_ENABLED:
                    speak(f"Switched to {config['name']}")
            else:
                print(f"❌ Mode '{mode_name}' not found. Available: normal, professional, talking, idle, emergency")
        return

    # Show memory
    if command == "show memory":
        if require_owner():
            handle_show_memory()
        return

    # Version
    if command == "version":
        handle_version()
        return

    # Show session
    if command == "show session":
        handle_show_session()
        return

    # Exit
    if command == "exit":
        print("Goodbye!")
        return

    # =========================
    # Route by Intent
    # =========================
    if route["intent"] == "command":
        # Commands are handled by the existing handlers in brain.py
        pass

    elif route["intent"] == "greeting":
        from modules.personality.responses import random_greeting
        greeting = random_greeting()
        print("RAF:", greeting)
        add_message("assistant", greeting)
        if VOICE_ENABLED:
            speak(greeting)
        return

    elif route["intent"] == "memory":
        result = get_memory_statement(command) or get_remember_command(command)
        if result:
            if require_owner():
                handle_remember(result)
        return

    elif route["intent"] == "recall":
        from core.handlers.recall_handler import handle_recall
        result = get_recall_command(command)
        if result:
            handle_recall(result)
        return

    elif route["intent"] == "personal":
        recall_result = get_recall_command(command)
        if recall_result:
            handle_recall(recall_result)
            return

    elif route["intent"] == "personal_blocked":
        print("RAF:", route["message"])
        add_message("assistant", route["message"])
        if VOICE_ENABLED:
            speak(route["message"])
        return

    elif route["intent"] == "calendar":
        prompt = build_prompt(command)
        response = generate_response(prompt)
        add_message("assistant", response)
        print("RAF:", response)
        if VOICE_ENABLED:
            speak(response)
        return

    elif route["intent"] == "search":
        result = search(command)
        print("RAF:", result)
        add_message("assistant", result)
        if VOICE_ENABLED:
            speak(result)
        return

    elif route["intent"] == "self_question":
        command_lower = command.lower()
        if "name" in command_lower:
            response = "My name is RAF — Revolutionary Artificial Friend."
        elif "internet" in command_lower or "online" in command_lower:
            response = "Yes, I can search the internet when you ask me to. I use DuckDuckGo for searches."
        else:
            response = "I'm RAF, your revolutionary artificial friend. I'm here to help."
        print("RAF:", response)
        add_message("assistant", response)
        if VOICE_ENABLED:
            speak(response)
        return

    elif route["intent"] == "mode_switch":
        from modules.modes.mode import set_mode, get_mode_config
        parts = command.split()
        if len(parts) == 2:
            mode_name = parts[1]
            if set_mode(mode_name):
                config = get_mode_config()
                print(f"✅ Mode switched to: {config['name']}")
                print(f"   {config['description']}")
                if VOICE_ENABLED:
                    speak(f"Switched to {config['name']}")
            else:
                print(f"❌ Mode '{mode_name}' not found. Available modes: normal, professional, talking, idle, emergency")
        return

    elif route["intent"] == "emotion":
        from core.handlers.emotion_handler import handle_emotion
        handle_emotion(route["emotion"])
        return

    elif route["intent"] == "mood":
        from core.handlers.mood_handler import handle_mood
        response = handle_mood()
        if response and VOICE_ENABLED:
            speak(response)
        return

    elif route["intent"] == "conversation":
        prompt = build_prompt(command)
        response = generate_response(prompt)
        add_message("assistant", response)
        print("RAF:", response)
        if VOICE_ENABLED:
            speak(response)
        return

    # =========================
    # Session
    # =========================
    add_command()

    # =========================
    # Greeting
    # =========================

    if handle_greeting(command):
        from modules.personality.responses import random_greeting
        greeting = random_greeting()
        print("RAF:", greeting)
        add_message("assistant", greeting)
        if VOICE_ENABLED:
            speak(greeting)
        return

    # =========================
    # Identity
    # =========================

    if handle_identity(command):
        return

    if handle_override(command):
        return

    # =========================
    # Natural Language Memory
    # =========================

    result = get_memory_statement(command)
    if result:
        if require_owner():
            handle_remember(result)
        return

    # =========================
    # Manual Remember
    # =========================

    remember_result = get_remember_command(command)
    if remember_result:
        if require_owner():
            handle_remember(remember_result)
        return

    # =========================
    # Recall
    # =========================

    recall_result = get_recall_command(command)
    if recall_result:
        handle_recall(recall_result)
        return

    # =========================
    # Mood
    # =========================

    if get_mood_command(command):
        handle_mood()
        return

    # =========================
    # Last Message
    # =========================

    if get_last_message_command(command):
        handle_last_message()
        return

    # =========================
    # Forget
    # =========================

    if command.startswith("forget "):
        if require_owner():
            handle_forget(command)
        return

    # =========================
    # Show Memory
    # =========================

    if command == "show memory":
        if require_owner():
            handle_show_memory()
        return

    # =========================
    # Version
    # =========================

    if command == "version":
        handle_version()
        return

    # =========================
    # Show Session
    # =========================

    if command == "show session":
        handle_show_session()
        return

    # =========================
    # Show Experiences
    # =========================

    if command == "show experiences":
        from modules.memory.experience import get_recent
        print()
        print("========== Recent Experiences ==========")
        for i, exp in enumerate(get_recent(), start=1):
            print(f"{i}. {exp}")
        return

    # =========================
    # Show Today
    # =========================

    if command == "show today":
        from modules.memory.daily_memory import get_today
        print()
        print("========== Today ==========")
        for item in get_today():
            print("-", item)
        return

    # =========================
    # Show Yesterday
    # =========================

    if command == "show yesterday":
        from modules.memory.daily_memory import get_yesterday
        print()
        print("========== Yesterday ==========")
        yesterday = get_yesterday()
        if not yesterday:
            print("No memories from yesterday.")
        else:
            for item in yesterday:
                print("-", item)
        return

    # =========================
    # Search Memories
    # =========================

    if command.startswith("find "):
        from modules.memory.experience import search_experiences
        from modules.memory.daily_memory import search_daily
        keyword = command[5:].strip()
        experiences = search_experiences(keyword)
        daily = search_daily(keyword)
        print()
        print(f"========== Search: {keyword} ==========")
        print()
        print(f"Experience Matches : {len(experiences)}")
        print(f"Daily Matches      : {len(daily)}")
        print(f"Total Matches      : {len(experiences) + len(daily)}")
        if not experiences and not daily:
            print("No matching memories found.")
            return
        if experiences:
            print("\nExperiences:")
            for i, item in enumerate(experiences, start=1):
                print(f"{i}. {item}")
        if daily:
            print("\nDaily Journal:")
            for day, item in daily:
                print(f"[{day}] {item}")
        return

    # =========================
    # Emotion Detection
    # =========================

    emotion = detect_emotion(command)
    if emotion != "neutral":
        set_reason(command)
        set_emotion(emotion)
        handle_emotion(get_emotion())
        return

    # =========================
    # Calendar / Date Questions
    # =========================

    from modules.calendar.calendar import find_calendar_event_in_text
    calendar_event = find_calendar_event_in_text(command)
    if calendar_event:
        if USE_LLM:
            prompt = build_prompt(command)
            print()
            response = generate_response(prompt)
            add_message("assistant", response)
            print("RAF:", response)
            if VOICE_ENABLED:
                speak(response)
            return

    # =========================
    # Personal Memory Grounding
    # =========================

    grounding = grounding_response(command)
    if grounding:
        print("RAF:", grounding)
        add_message("assistant", grounding)
        if VOICE_ENABLED:
            speak(grounding)
        return

    # =========================
    # Continue Conversation
    # =========================

    if handle_conversation(command):
        return

    # =========================
    # Unknown
    # =========================

    if USE_LLM:
        prompt = build_prompt(command)
        print()
        response = generate_response(prompt)
        add_message("assistant", response)
        print("RAF:", response)
        if VOICE_ENABLED:
            speak(response)
    else:
        handle_unknown()