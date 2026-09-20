"""
RAF Self Handler for PROJECT R1
Handles questions about RAF itself.
Examples: "who are you", "how are you", "what can you do"
"""


def handle_raf_self(command):
    """
    Handle a RAF self-question.
    Returns True if handled, False otherwise.
    """
    command = command.strip().lower()
    
    if not command:
        return False
    
    # =========================
    # Match against RAF_SELF_ANSWERS
    # =========================
    from modules.llm.llm import RAF_SELF_ANSWERS
    
    # Try exact match first
    if command in RAF_SELF_ANSWERS:
        _reply(RAF_SELF_ANSWERS[command])
        return True
    
    # Try partial match
    for key, answer in RAF_SELF_ANSWERS.items():
        if key in command or command in key:
            _reply(answer)
            return True
    
    # =========================
    # Fallback for variations
    # =========================
    # Greeting-style variations
    if command in ["how are you doing", "how's it going", "how you doing"]:
        _reply("I'm doing great! How can I help you?")
        return True
    
    if command in ["what is your name", "what's your name"]:
        _reply("My name is RAF — Revolutionary Artificial Friend.")
        return True
    
    if command in ["who made you", "who built you"]:
        _reply("I was created by Aditya, a brilliant developer with a vision.")
        return True
    
    # Not a RAF self question
    return False


# =========================
# HELPER
# =========================

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