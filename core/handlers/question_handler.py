"""
Question Handler for PROJECT R1
Handles general knowledge and factual questions.
Flow: permanent memory → memory.json → Mem0 → SearXNG → LLM fallback
"""


def handle_question(command):
    """
    Handle a factual question.
    Returns True if handled, False otherwise.
    """
    command = command.strip().lower()
    
    if not command:
        return False
    
    # =========================
    # LAYER 1: permanent_memory (family)
    # =========================
    response = _search_permanent(command)
    if response:
        _reply(response)
        return True
    
    # =========================
    # LAYER 2: memory.json (personal facts)
    # =========================
    response = _search_memory_json(command)
    if response:
        _reply(response)
        return True
    
    # =========================
    # LAYER 3: Mem0 (only if high confidence)
    # =========================
    response = _search_mem0(command)
    if response:
        _reply(response)
        return True
    
    # =========================
    # LAYER 4: SearXNG (general knowledge)
    # =========================
    response = _search_online(command)
    if response:
        _reply(response)
        return True
    
    # =========================
    # LAYER 5: LLM fallback
    # =========================
    response = _search_llm(command)
    if response:
        _reply(response)
        return True
    
    # =========================
    # NOTHING FOUND
    # =========================
    _reply("I couldn't find an answer to that. Could you rephrase?")
    return True


# =========================
# HELPERS
# =========================

def _search_permanent(command):
    """
    Check permanent memory for family-related facts.
    Only matches if the command mentions a family keyword.
    """
    try:
        from modules.memory.permanent_memory import search_permanent
        from modules.memory.memory import load_memory
        
        # Extract meaningful words from command
        keywords = command.split()
        
        # Only look for family-related words
        family_terms = {
            "dad", "mom", "father", "mother", "sister", "brother",
            "grandfather", "grandmother", "grandpa", "grandma",
            "family", "pet", "wife", "husband", "son", "daughter",
        }
        
        # Check if any family term is in command
        matched = None
        for term in family_terms:
            if term in keywords:
                matched = term
                break
        
        if not matched:
            return None
        
        # Search permanent memory with the matched term
        results = search_permanent(matched)
        if results:
            memories = [m["fact"] for m in results]
            # Deduplicate
            unique = list(dict.fromkeys(memories))
            if len(unique) == 1:
                return f"Here's what I know: {unique[0]}"
            return "Here's what I know: " + " | ".join(unique)
        
        return None
    except Exception:
        return None


def _search_memory_json(command):
    """
    Check memory.json for personal facts mentioned in the command.
    """
    try:
        from modules.memory.memory import load_memory
        
        memory_data = load_memory()
        command_words = command.lower().split()
        
        for key, value in memory_data.items():
            # Get key words (handle underscores and apostrophes)
            key_words = key.replace("_", " ").replace("'s", "").split()
            
            # Check if any key word appears in the command
            for kw in key_words:
                if len(kw) > 2 and kw in command_words:
                    if isinstance(value, dict):
                        value = value.get("value")
                    
                    display = key.replace("_", " ").strip()
                    if display.startswith("my "):
                        display = display[3:]
                    return f"Your {display} is {value}."
        
        return None
    except Exception:
        return None


def _search_mem0(command):
    """
    Search Mem0 — only use if score > 0.6 (high confidence).
    """
    try:
        from modules.memory.mem0_memory import search_memory
        
        results = search_memory(command, user_id="aditya", limit=3)
        
        if isinstance(results, dict):
            results = results.get("results", [])
        
        if not results:
            return None
        
        # Only use high-confidence memories
        good = [r for r in results if r.get("score", 0) > 0.6]
        
        if not good:
            return None
        
        memories = [r.get("memory", "") for r in good if r.get("memory")]
        
        if memories:
            return "Here's what I remember: " + " | ".join(memories[:2])
        
        return None
    except Exception:
        return None


def _search_online(command):
    """
    Search SearXNG (local) for the answer.
    """
    try:
        from modules.internet.searxng_search import searxng_search
        
        result = searxng_search(command)
        
        if result and len(result) > 5:
            return result
        
        return None
    except Exception:
        return None


def _search_llm(command):
    """
    Fallback: use LLM directly for the answer.
    """
    try:
        from modules.prompting.prompt_builder import build_prompt
        from modules.llm.llm import generate_response
        
        prompt = build_prompt(command)
        response = generate_response(prompt, user_message=command)
        
        if response and len(response) > 5:
            return response
        
        return None
    except Exception:
        return None


def _reply(response):
    """
    Print response + log to conversation + voice output.
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