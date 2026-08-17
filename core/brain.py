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
from core.handlers.version_handler import handle_version
from config import USE_LLM
from modules.llm.llm import generate_response
from modules.prompting.prompt_builder import build_prompt
from modules.conversation.context import (
    add_message,
    get_recent_history
)

def process_command(command):

    # =========================
    # Session
    # =========================

    add_command()
    command = command.strip().lower()
    add_message("user", command)

    # =========================
    # Greeting
    # =========================

    if handle_greeting(command):
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
    else:

        handle_unknown()