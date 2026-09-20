"""
Personal Handler for PROJECT R1
Handles personal questions about Aditya, family, and friends.
Examples: "what is my name", "tell me about my dad", "do you remember my grandfather"

CRITICAL RULE: Personal questions stay personal.
If not found in any memory layer → "I don't remember that yet, bro."
Never falls through to search.
"""


def handle_personal(command):
    """
    Handle a personal question.
    Returns True if handled, False otherwise.
    """
    command = command.strip().lower()
    
    if not command:
        return False
    
    # =========================
    # SPECIAL CASE: "who is in my family" / "my family"
    # =========================
    if any(phrase in command for phrase in ["who is in my family", "who is my family", "list my family", "my family", "show my family"]):
        return _show_family_list()
    
    # =========================
    # SPECIAL CASE: "who am i" / "tell me about myself"
    # =========================
    if command in ["who am i", "tell me about myself", "tell me about me", "what do you know about me"]:
        return _about_me()
    
    # =========================
    # FRIEND QUESTIONS: "tell me about my friend X" / "who is my friend X"
    # =========================
    if "friend" in command:
        return _handle_friend_question(command)
    
    # =========================
    # EXTRACT KEY
    # =========================
    from modules.language.language import get_personal_lookup
    key = get_personal_lookup(command)
    
    if not key:
        return False
    
    # =========================
    # LAYER 1: memory.json (personal facts)
    # =========================
    response = _search_memory_json(key)
    if response:
        _reply(response)
        return True
    
    # =========================
    # LAYER 2: permanent_memory (family)
    # =========================
    response = _search_permanent(key)
    if response:
        _reply(response)
        return True
    
    # =========================
    # LAYER 3: Mem0 (friends, stories)
    # =========================
    response = _search_mem0(command)
    if response:
        _reply(response)
        return True
    
    # =========================
    # NOT FOUND
    # =========================
    display_key = key.replace("my_", "").replace("_", " ").strip()
    _reply(f"I don't remember your {display_key} yet, bro.")
    return True


# =========================
# HELPERS
# =========================

def _search_memory_json(key):
    """
    Search memory.json with multi-format key matching.
    """
    try:
        from modules.memory.memory import load_memory
        memory_data = load_memory()
        
        # Try multiple key formats
        for test_key in [
            key,
            key.replace("my_", ""),
            f"my_{key}",
            key.replace("'s", ""),
            f"{key}'s_name",
        ]:
            if test_key in memory_data:
                value = memory_data[test_key]
                if isinstance(value, dict):
                    value = value.get("value")
                display = test_key.replace("_", " ").replace("'s", "'s").strip()
                if display.startswith("my "):
                    display = display[3:]
                return f"Your {display} is {value}."
        
        return None
    except Exception:
        return None


def _search_permanent(key):
    """
    Search permanent_memory for family facts.
    """
    try:
        from modules.memory.permanent_memory import search_permanent
        search_term = key.replace("my_", "").replace("_", " ").strip()
        results = search_permanent(search_term)
        
        if results:
            memories = [m["fact"] for m in results]
            if len(memories) == 1:
                return f"Here's what I know: {memories[0]}"
            return "Here's what I know: " + " | ".join(memories)
        
        return None
    except Exception:
        return None


def _search_mem0(command):
    """
    Search Mem0 for personal/friend memories.
    """
    try:
        from modules.memory.mem0_memory import search_memory
        results = search_memory(command, user_id="aditya", limit=3)
        
        if isinstance(results, dict):
            results = results.get("results", [])
        
        if results:
            memories = [r.get("memory", "") for r in results if r.get("memory")]
            # Filter out very low scores
            good = [r for r in results if r.get("score", 0) > 0.4]
            if good:
                memories = [r.get("memory", "") for r in good if r.get("memory")]
                if memories:
                    return "Here's what I remember: " + " | ".join(memories[:3])
        
        return None
    except Exception:
        return None


def _show_family_list():
    """
    Show all family memories.
    """
    try:
        from modules.memory.permanent_memory import get_family
        family = get_family()
        
        if not family:
            _reply("I don't have any family memories yet.")
            return True
        
        # Deduplicate by fact
        seen = set()
        unique = []
        for m in family:
            fact = m["fact"]
            if fact not in seen:
                seen.add(fact)
                unique.append(fact)
        
        _reply("Here's your family: " + " | ".join(unique))
        return True
    except Exception as e:
        _reply(f"Error showing family: {e}")
        return True


def _about_me():
    """
    Answer "who am i" / "tell me about myself".
    """
    try:
        from modules.memory.memory import load_memory
        memory_data = load_memory()
        
        name = memory_data.get("name", "you")
        age = memory_data.get("age", "")
        city = memory_data.get("my_city", "") or memory_data.get("city", "")
        
        parts = [f"Your name is {name}."]
        if age:
            parts.append(f"You're {age} years old.")
        if city:
            parts.append(f"You live in {city}.")
        
        _reply(" ".join(parts))
        return True
    except Exception:
        _reply("I don't know much about you yet.")
        return True


def _handle_friend_question(command):
    """
    Handle "tell me about my friend X" / "who is my friend X".
    """
    import re
    
    # Extract friend name
    match = re.search(r'friend\s+(\w+)', command)
    specific_name = match.group(1) if match else None
    
    try:
        from modules.memory.mem0_memory import search_memory
        results = search_memory(command, user_id="aditya", limit=20)
        
        if isinstance(results, dict):
            results = results.get("results", [])
        
        # Filter friend memories
        friend_memories = []
        for r in results:
            mem = r.get("memory", "")
            mem_lower = mem.lower()
            if "friend" in mem_lower:
                if specific_name:
                    if specific_name in mem_lower:
                        friend_memories.append(mem)
                else:
                    friend_memories.append(mem)
        
        if friend_memories:
            if specific_name:
                _reply(f"Here's what I remember about {specific_name.title()}: " + " | ".join(friend_memories[:5]))
            else:
                _reply("Here's what I remember about your friends: " + " | ".join(friend_memories[:5]))
        else:
            if specific_name:
                _reply(f"I don't have any memories about {specific_name.title()} yet.")
            else:
                _reply("I don't have any memories about your friends yet.")
        
        return True
    except Exception:
        _reply("I couldn't search friend memories right now.")
        return True


def _reply(response):
    """
    Print response + add to conversation history + voice output.
    """
    print("RAF:", response)
    
    try:
        from modules.conversation.context import add_message
        add_message("assistant", response)
    except Exception:
        pass
    
    try:
        from config import VOICE_ENABLED
        if VOICE_ENABLED:
            from modules.voice.voice import speak
            speak(response)
    except Exception:
        pass