"""
Statement Handler for PROJECT R1
Handles statements where the user shares information.
Examples: "my dad is Rajesh", "I like pizza", "remember my project is R1"
"""


def handle_statement(command):
    """
    Handle a statement (sharing info).
    Stores in memory.json + permanent_memory (if family) + Mem0.
    Returns True if handled, False otherwise.
    """
    command = command.strip().lower()
    
    if not command:
        return False
    
    # =========================
    # Extract key/value from statement
    # =========================
    from modules.language.language import get_memory_statement, get_remember_command
    
    result = get_memory_statement(command) or get_remember_command(command)
    
    if not result:
        # Not a parseable statement — fall back to Mem0-only storage
        return _store_in_mem0_only(command)
    
    key = result.get("key", "").strip()
    value = result.get("value", "").strip()
    
    if not key or not value:
        return _store_in_mem0_only(command)
    
    # =========================
    # Check owner permission
    # =========================
    from core.handlers.owner_handler import require_owner
    if not require_owner():
        return True  # handled (blocked)
    
    # =========================
    # Store in memory.json
    # =========================
    from modules.memory.memory import remember
    remember(key, value)
    
    # =========================
    # Check if family-related → also store in permanent_memory
    # =========================
    family_keywords = [
        "dad", "mom", "father", "mother", "brother", "sister",
        "family", "grandma", "grandpa", "grandmother", "grandfather",
        "uncle", "aunt", "cousin", "son", "daughter", "wife", "husband",
        "pet",
    ]
    is_family = any(kw in key.lower() for kw in family_keywords)
    
    if is_family:
        try:
            from modules.memory.permanent_memory import add_permanent
            # Format: "dad's name: rajesh" or "mom: sunita"
            fact_text = f"{key.replace('_', ' ')}: {value}"
            add_permanent(fact_text, category="family")
        except Exception as e:
            print(f"⚠️ Permanent memory error: {e}")
    
    # =========================
    # Store in Mem0 (automatic extraction)
    # =========================
    try:
        from modules.memory.mem0_memory import add_memory
        add_memory([
            {"role": "user", "content": command}
        ], user_id="aditya")
    except Exception:
        pass  # Silent fail — Mem0 is optional
    
    # =========================
    # Confirm
    # =========================
    display_key = key.replace("_", " ").strip()
    response = f"Got it, I'll remember that your {display_key} is {value}."
    print("RAF:", response)
    
    # Voice output if enabled
    try:
        from config import VOICE_ENABLED
        if VOICE_ENABLED:
            from modules.voice.voice import speak
            speak(response)
    except Exception:
        pass
    
    return True


def _store_in_mem0_only(command):
    """
    If the statement couldn't be parsed into key/value,
    still send it to Mem0 for automatic extraction.
    """
    try:
        from modules.memory.mem0_memory import add_memory
        add_memory([
            {"role": "user", "content": command}
        ], user_id="aditya")
        
        response = "Got it, I'll remember that."
        print("RAF:", response)
        
        try:
            from config import VOICE_ENABLED
            if VOICE_ENABLED:
                from modules.voice.voice import speak
                speak(response)
        except Exception:
            pass
        
        return True
    except Exception:
        return False