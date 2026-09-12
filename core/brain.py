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
    get_last_message_command,
    get_personal_lookup
)

# =========================
# Mem0 — Permanent Memory
# =========================

from modules.memory.mem0_memory import add_memory, search_memory

# =========================
# Other Imports
# =========================

from core.handlers.version_handler import handle_version
from config import USE_LLM
from config import VOICE_ENABLED
from modules.voice.voice import speak
from modules.llm.llm import generate_response, RAF_SELF_ANSWERS
from modules.prompting.prompt_builder import build_prompt
from modules.conversation.context import (
    add_message,
    get_recent_history
)
from modules.internet.search import search
from modules.grounding.grounding import grounding_response
from modules.routing.intent_router import IntentRouter
from modules.memory.permanent_memory import add_permanent, get_family, get_identity


def process_command(command):
    command = command.strip().lower()
    add_message("user", command)

    # =========================
    # FAST COMMANDS — bypass LLM (MUST BE FIRST)
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

    # Show family
    if command == "show family":
        from modules.memory.mem0_memory import search_memory
        from modules.memory.permanent_memory import get_family
        print()
        print("========== Family Memories ==========")
        # Permanent family memories
        permanent = get_family()
        if permanent:
            print("\n📌 Permanent:")
            for m in permanent:
                print(f"  - {m['fact']}")
        # Mem0 semantic search for family
        try:
            results = search_memory("family members parents siblings grandparents", user_id="aditya", limit=20)
            if isinstance(results, dict):
                results = results.get("results", [])
            if results:
                print("\n🧠 From Conversation:")
                for r in results:
                    if r.get("memory"):
                        print(f"  - {r['memory']}")
        except Exception:
            pass
        if not permanent and not results:
            print("No family memories yet.")
        print()
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
    # "Did you mean?" Auto-correct — MUST RUN BEFORE ROUTER
    # =========================

    print(f"🔍 BEFORE AUTO-CORRECT: command='{command}'")  # DEBUG

    from modules.language.suggestions import suggest_correction
    suggestion = suggest_correction(command)
    if suggestion:
        print(f"🔧 Auto-corrected to: '{suggestion}'")
        command = suggestion

    print(f"🔍 AFTER AUTO-CORRECT: command='{command}'")  # DEBUG

    # =========================
    # Intelligence Router
    # =========================
    router = IntentRouter()
    route = router.route(command)

    # =========================
    # Route by Intent
    # =========================
    if route["intent"] == "fast_answer":
        from modules.llm.llm import RAF_SELF_ANSWERS
        key = route.get("key")
        answer = None
        if key and key in RAF_SELF_ANSWERS:
            answer = RAF_SELF_ANSWERS[key]
        else:
            for k, v in RAF_SELF_ANSWERS.items():
                if k in command:
                    answer = v
                    break
        if answer:
            print("RAF:", answer)
            add_message("assistant", answer)
            if VOICE_ENABLED:
                speak(answer)
            # Add to Mem0
            try:
                add_memory([
                    {"role": "user", "content": command},
                    {"role": "assistant", "content": answer}
                ], user_id="aditya")
            except Exception:
                pass
        return

    elif route["intent"] == "multi_part":
        parts = command.split(" and ")
        responses = []
        from modules.llm.llm import RAF_SELF_ANSWERS
        from modules.memory.memory import recall
        for part in parts:
            part = part.strip()
            found = False
            for key in RAF_SELF_ANSWERS:
                if key in part:
                    responses.append(RAF_SELF_ANSWERS[key])
                    found = True
                    break
            if not found:
                from modules.language.language import get_recall_command
                recall_result = get_recall_command(part)
                if recall_result:
                    key = recall_result.get("key")
                    if key:
                        value = recall(key)
                        if value:
                            responses.append(f"Your {key.replace('_', ' ')} is {value}.")
                            found = True
            if not found:
                responses.append(f"I'm not sure about '{part}'.")
        combined = " ".join(responses)
        print("RAF:", combined)
        add_message("assistant", combined)
        if VOICE_ENABLED:
            speak(combined)
        try:
            add_memory([
                {"role": "user", "content": command},
                {"role": "assistant", "content": combined}
            ], user_id="aditya")
        except Exception:
            pass
        return

    elif route["intent"] == "personal_lookup":
        from modules.memory.memory import recall
        from modules.memory.mem0_memory import search_memory
        from modules.memory.permanent_memory import search_permanent
        
        key = route["key"]
        response = None
        
        # Extract search term from key
        search_term = key.replace("my_", "").replace("_", " ")
        
        # =========================
        # STEP 1: Search permanent memory (exact matches)
        # =========================
        permanent_results = search_permanent(search_term)
        if permanent_results:
            memories = [m["fact"] for m in permanent_results]
            response = "Here's what I know: " + " | ".join(memories)
        
        # =========================
        # STEP 2: Try old memory system
        # =========================
        if not response:
            value = recall(key)
            if value:
                display_key = key.replace("_", " ").strip()
                if display_key.startswith("my "):
                    display_key = display_key[3:]
                response = f"Your {display_key} is {value}."
        
        # =========================
        # STEP 3: Try Mem0
        # =========================
        if not response:
            try:
                mem0_results = search_memory(command, user_id="aditya", limit=3)
                if isinstance(mem0_results, dict):
                    results = mem0_results.get("results", [])
                else:
                    results = mem0_results
                if results:
                    memories = [r.get("memory", "") for r in results if r.get("memory")]
                    if memories:
                        response = "Here's what I remember: " + " | ".join(memories[:3])
            except Exception:
                pass
        
        # =========================
        # STEP 4: Fallback
        # =========================
        if not response:
            display_key = key.replace("_", " ").strip()
            if display_key.startswith("my "):
                display_key = display_key[3:]
            response = f"I don't remember your {display_key} yet."
        
        print("RAF:", response)
        add_message("assistant", response)
        if VOICE_ENABLED:
            speak(response)
        return

    elif route["intent"] == "memory_search":
        from modules.memory.permanent_memory import get_family, get_identity, search_permanent
        from modules.memory.mem0_memory import search_memory
        
        response = None
        
        # =========================
        # SPECIAL CASE: "who is in my family" / "my family"
        # =========================
        if "family" in command.lower():
            family = get_family()
            if family:
                memories = [m["fact"] for m in family]
                response = "Here's your family: " + " | ".join(memories)
            else:
                response = "I don't have any family memories yet."
            print("RAF:", response)
            add_message("assistant", response)
            if VOICE_ENABLED:
                speak(response)
            return
        # =========================
        # FRIENDS — use Mem0 semantic search with filter
        # =========================
        if "friend" in command.lower():
            try:
                mem0_results = search_memory(command, user_id="aditya", limit=20)
                if isinstance(mem0_results, dict):
                    results = mem0_results.get("results", [])
                else:
                    results = mem0_results
                
                # Check if a specific friend name is mentioned
                # Extract name after "friend " 
                import re
                name_match = re.search(r'friend\s+(\w+)', command.lower())
                specific_name = name_match.group(1) if name_match else None
                
                # Filter friend memories
                friend_memories = []
                for r in results:
                    mem = r.get("memory", "")
                    mem_lower = mem.lower()
                    if "friend" in mem_lower:
                        # If a specific name is mentioned, only include that person
                        if specific_name:
                            if specific_name in mem_lower:
                                friend_memories.append(mem)
                        else:
                            friend_memories.append(mem)
                
                if friend_memories:
                    if specific_name:
                        response = f"Here's what I remember about {specific_name.title()}: " + " | ".join(friend_memories[:5])
                    else:
                        response = "Here's what I remember about your friends: " + " | ".join(friend_memories[:5])
                else:
                    if specific_name:
                        response = f"I don't have any memories about {specific_name.title()} yet."
                    else:
                        response = "I don't have any memories about your friends yet."
            except Exception:
                response = "I don't have any memories about your friends yet."
            print("RAF:", response)
            add_message("assistant", response)
            if VOICE_ENABLED:
                speak(response)
            return

        # =========================
        # OTHERWISE: Search by relationship
        # =========================
        relationship_keywords = {
            # Check longer words FIRST (grandfather before father)
            "grandfather": "grandfather", "grandpa": "grandfather",
            "grandmother": "grandmother", "grandma": "grandmother",
            "sister": "sister", "brother": "brother",
            "father": "dad", "dad": "dad",
            "mother": "mom", "mom": "mom",
        }
        
        matched_keyword = None
        command_lower = command.lower()
        for keyword, canonical in relationship_keywords.items():
            if keyword in command_lower:
                matched_keyword = canonical
                break
        
        # Search permanent memory
        permanent_results = search_permanent(matched_keyword if matched_keyword else command)
        
        if permanent_results:
            memories = [m["fact"] for m in permanent_results]
            response = "Here's what I know: " + " | ".join(memories)
        
        # Step 2: If no permanent match, try Mem0
        if not response:
            try:
                mem0_results = search_memory(command, user_id="aditya", limit=3)
                if isinstance(mem0_results, dict):
                    results = mem0_results.get("results", [])
                else:
                    results = mem0_results
                if results:
                    memories = [r.get("memory", "") for r in results if r.get("memory")]
                    if memories:
                        response = "Here's what I remember: " + " | ".join(memories[:3])
            except Exception:
                pass
        
        # Step 3: Fallback
        if not response:
            response = "I don't have any memories about that yet."
        
        print("RAF:", response)
        add_message("assistant", response)
        if VOICE_ENABLED:
            speak(response)
        return

    elif route["intent"] == "command":
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
            # Also store in permanent memory if it's a family fact
            try:
                key = result.get("key", "")
                value = result.get("value", "")
                # Check if it's a family-related fact
                family_keywords = ["dad", "mom", "father", "mother", "brother", "sister",
                                   "family", "grandma", "grandpa", "uncle", "aunt", "cousin"]
                if any(kw in key.lower() or kw in value.lower() for kw in family_keywords):
                    add_permanent(f"{key.replace('_', ' ')}: {value}", category="family")
            except Exception:
                pass
        return

    elif route["intent"] == "friend_memory":
        # Store friend fact using existing memory statement parser
        result = get_memory_statement(command)
        if result:
            if require_owner():
                handle_remember(result)
            # Also add to Mem0 explicitly
            try:
                from modules.memory.mem0_memory import add_memory
                add_memory([
                    {"role": "user", "content": command}
                ], user_id="aditya")
            except Exception:
                pass
        else:
            # Fallback: store the whole sentence
            print("RAF: Got it, I'll remember that.")
            try:
                from modules.memory.mem0_memory import add_memory
                add_memory([
                    {"role": "user", "content": command}
                ], user_id="aditya")
            except Exception:
                pass
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
        response = generate_response(prompt, user_message=command)
        add_message("assistant", response)
        print("RAF:", response)
        if VOICE_ENABLED:
            speak(response)
        try:
            add_memory([
                {"role": "user", "content": command},
                {"role": "assistant", "content": response}
            ], user_id="aditya")
        except Exception:
            pass
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

    elif route["intent"] == "emotion":
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
        response = generate_response(prompt, user_message=command)
        add_message("assistant", response)
        print("RAF:", response)
        if VOICE_ENABLED:
            speak(response)
        # =========================
        # Add to Mem0 (automatic extraction)
        # =========================
        try:
            add_memory([
                {"role": "user", "content": command},
                {"role": "assistant", "content": response}
            ], user_id="aditya")
        except Exception:
            pass
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
            response = generate_response(prompt, user_message=command)
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
        response = generate_response(prompt, user_message=command)
        add_message("assistant", response)
        print("RAF:", response)
        if VOICE_ENABLED:
            speak(response)
        # Add to Mem0
        try:
            add_memory([
                {"role": "user", "content": command},
                {"role": "assistant", "content": response}
            ], user_id="aditya")
        except Exception:
            pass
    else:
        handle_unknown()