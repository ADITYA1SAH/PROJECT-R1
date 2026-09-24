"""
Chat Handler for PROJECT R1
Handles greetings and casual conversation.
Flow: greeting (cache) OR LLM → Mem0
"""


def handle_chat(command):
    """
    Handle a chat/greeting.
    Returns True if handled, False otherwise.
    """
    command = command.strip().lower()
    
    if not command:
        return False
    
    # =========================
    # GREETINGS — exact match
    # =========================
    # Strip punctuation
    clean = command.rstrip("?!.,").strip()
    
    # Time-specific greetings
    time_greetings = {
        "good morning": ["Good morning, bro!", "Morning! Ready to start the day?", "Hey, good morning!"],
        "good afternoon": ["Good afternoon!", "Hey, hope your day's going well.", "Afternoon, bro!"],
        "good evening": ["Good evening!", "Hey, evening vibes!", "Good evening, Aditya."],
        "good night": ["Good night, bro! Sleep well.", "Night! Rest up.", "Sweet dreams, Aditya."],
    }
    
    if clean in time_greetings:
        import random
        response = random.choice(time_greetings[clean])
        _reply(response)
        return True
    
    # General greetings
    greetings = {"hi", "hello", "hey", "yo", "sup", "wassup"}
    
    if clean in greetings:
        from modules.personality.responses import random_greeting
        response = random_greeting()
        _reply(response)
        return True
    
    # =========================
    # GOODBYES — exact match
    # =========================
    goodbyes = {"bye", "goodbye", "see you", "see ya", "later"}
    if clean in goodbyes:
        response = "See you later, bro!"
        _reply(response)
        return True
    
    # =========================
    # THANKS — exact match
    # =========================
    thanks = {"thanks", "thank you", "ty", "thx"}
    if clean in thanks:
        response = "Anytime, bro!"
        _reply(response)
        return True
    
    # =========================
    # EVERYTHING ELSE — LLM
    # =========================
    return _chat_with_llm(command)


# =========================
# HELPERS
# =========================

def _chat_with_llm(command):
    """
    Send to LLM for casual conversation.
    Also stores in Mem0 for future reference.
    """
    try:
        from modules.prompting.prompt_builder import build_prompt
        from modules.llm.llm import generate_response
        
        prompt = build_prompt(command)
        response = generate_response(prompt, user_message=command)
        
        if not response:
            response = "Hmm, I'm not sure what to say to that."
        
        _reply(response)
        
        # Store in Mem0 (automatic extraction)
        try:
            from modules.memory.mem0_memory import add_memory
            add_memory([
                {"role": "user", "content": command},
                {"role": "assistant", "content": response}
            ], user_id="aditya")
        except Exception:
            pass  # Silent fail — Mem0 is optional
        
        return True
    except Exception as e:
        print(f"⚠️ Chat error: {e}")
        _reply("I'm having trouble processing that right now.")
        return True


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