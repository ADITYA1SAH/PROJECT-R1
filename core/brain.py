"""
Main Brain for PROJECT R1
Clean orchestrator — routes commands to handlers based on query type.
"""

from modules.routing.query_classifier import classify_query
from modules.conversation.context import add_message


# =========================
# HANDLER REGISTRY
# =========================
# Maps query type → handler function
# Order doesn't matter here — the classifier decides.

def _get_handler(query_type):
    """
    Return the handler function for a given query type.
    Returns None if no handler is registered.
    """
    if query_type == "command":
        from core.handlers.command_handler import handle_command
        return handle_command
    elif query_type == "statement":
        from core.handlers.statement_handler import handle_statement
        return handle_statement
    elif query_type == "personal":
        from core.handlers.personal_handler import handle_personal
        return handle_personal
    elif query_type == "raf_self":
        from core.handlers.raf_self_handler import handle_raf_self
        return handle_raf_self
    elif query_type == "weather":
        from core.handlers.weather_handler import handle_weather
        return handle_weather
    elif query_type == "question":
        from core.handlers.question_handler import handle_question
        return handle_question
    elif query_type == "chat":
        from core.handlers.chat_handler import handle_chat
        return handle_chat
    
    return None


def process_command(command):
    """
    Process a user command.
    This is the single entry point — clean and simple.
    """
    command = command.strip().lower()
    
    if not command:
        return
    
    # =========================
    # 1. Log user message
    # =========================
    add_message("user", command)
    
    # =========================
    # 2. Classify query type
    # =========================
    try:
        query_type = classify_query(command)
    except Exception as e:
        print(f"⚠️ Classification error: {e}")
        query_type = "chat"
    
    # =========================
    # 3. Get the handler
    # =========================
    handler = _get_handler(query_type)
    
    if handler is None:
        # Fallback to chat if no handler found
        from core.handlers.chat_handler import handle_chat
        handler = handle_chat
    
    # =========================
    # 4. Run the handler
    # =========================
    try:
        handled = handler(command)
        
        # If handler returned False → fallback to chat
        if not handled:
            from core.handlers.chat_handler import handle_chat
            handle_chat(command)
    except Exception as e:
        print(f"⚠️ Handler error: {e}")
        print("RAF: I'm having trouble processing that right now.")