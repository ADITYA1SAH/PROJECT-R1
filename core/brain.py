from core.handlers.memory_handler import handle_remember
from core.handlers.owner_handler import require_owner
from modules.memory.memory import remember, forget
from modules.session.session import (
    add_command,
    get_command_count,
    get_session_minutes
)
from modules.language.language import (
    get_memory_statement,
    get_remember_command,
    get_recall_command,
    get_mood_command,
    get_last_message_command
)
from modules.emotion.emotion import (
    detect_emotion,
    emotion_icon
)

from modules.emotion.responses import RESPONSES
from modules.emotion.state import (
    set_emotion,
    get_emotion
)
from modules.context.context import (
    set_last_message,
    get_last_message
)
from modules.emotion.reason import (
    set_reason,
    get_reason
)
from core.handlers.emotion_handler import handle_emotion
from core.handlers.forget_handler import handle_forget
from core.handlers.show_memory_handler import handle_show_memory
from core.handlers.session_handler import handle_show_session
from core.handlers.mood_handler import handle_mood
from core.handlers.last_message_handler import handle_last_message
from core.handlers.recall_handler import handle_recall
from core.handlers.unknown_handler import handle_unknown
from core.handlers.identity_handler import handle_identity
from core.handlers.override_handler import handle_override
from core.handlers.greeting_handler import handle_greeting
from core.handlers.conversation_handler import handle_conversation

def process_command(command):

    add_command()

    command = command.strip().lower()
    if handle_greeting(command):
        return
    
    if handle_conversation(command):
        return


    # Detect emotion
    emotion = detect_emotion(command)

    if emotion != "neutral":

        set_reason(command)
        set_emotion(emotion)

        handle_emotion(get_emotion())

        return

    if handle_identity(command):
        return
    if handle_override(command):
        return
    
    # Natural language memory
    result = get_memory_statement(command)

    if result:

        if require_owner():
            handle_remember(result)

        return


    # Manual remember command
    remember_result = get_remember_command(command)

    if remember_result:

        if require_owner():
            handle_remember(remember_result)

        return
    
    recall_result = get_recall_command(command)

    if recall_result:

        handle_recall(recall_result)

        return
    
    mood_result = get_mood_command(command)

    if mood_result:

        handle_mood()

        return
    
    last_message_result = get_last_message_command(command)

    if last_message_result:

        handle_last_message()

        return
    
    if command.startswith("forget "):

        if require_owner():
            handle_forget(command)

        return
    
    if command == "show memory":

        if require_owner():
            handle_show_memory()

        return
    
    if command == "show session":

        handle_show_session()

        return
    
    if command == "show experiences":

        from modules.memory.experience import get_recent

        print()

        print("========== Recent Experiences ==========")

        for i, exp in enumerate(get_recent(), start=1):

            print(f"{i}. {exp}")
            
        return
    if command == "show today":

        from modules.memory.daily_memory import get_today

        print()

        print("========== Today ==========")

        for item in get_today():

            print("-", item)

        return

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

    if command.startswith("find "):

        from modules.memory.experience import search_experiences
        from modules.memory.daily_memory import search_daily

        keyword = command[5:].strip()

        experiences = search_experiences(keyword)
        daily = search_daily(keyword)
        experience_count = len(experiences)
        daily_count = len(daily)
        total = experience_count + daily_count

        print()
        print(f"========== Search: {keyword} ==========")
        print()
        print(f"Experience Matches : {experience_count}")
        print(f"Daily Matches      : {daily_count}")
        print(f"Total Matches      : {total}")
        
        if not experiences and not daily:

            print("No matching memories found.")

        else:

            if experiences:

                print("\nExperiences:")

                for i, item in enumerate(experiences, start=1):

                    print(f"{i}. {item}")

            if daily:

                print("\nDaily Journal:")

                for day, item in daily:

                    print(f"[{day}] {item}")

        return

    handle_unknown()

    save_context(command)
    
def save_context(command):
    set_last_message(command)

