"""
Query Classifier for PROJECT R1
Distinguishes between: question, statement, chat
"""

import re


def classify_query(query):
    """
    Classify a query as:
    - "question"  → asking for information
    - "statement" → sharing information
    - "chat"      → casual conversation
    - "command"   → explicit command (show memory, version, etc.)
    """
    query_lower = query.lower().strip()
    
    # =========================
    # COMMANDS — highest priority
    # =========================
    command_patterns = [
        r"^show\s+",
        r"^find\s+",
        r"^forget\s+",
        r"^remember\s+",
        r"^mode\s+",
        r"^export\s+",
        r"^memory\s+maintenance",
        r"^clean\s+memory",
        r"^version$",
        r"^help$",
        r"^exit$",
    ]
    for pattern in command_patterns:
        if re.match(pattern, query_lower):
            return "command"
    
    # =========================
    # CHAT — greetings/casual only (exact match)
    # =========================
    chat_exact = [
        "hi", "hello", "hey", "yo",
        "good morning", "good afternoon", "good evening", "good night",
        "thanks", "thank you", "ok", "okay", "cool", "nice",
        "lol", "haha", "bye", "goodbye",
    ]
    if query_lower.rstrip("!?.") in chat_exact:
        return "chat"
    
    # =========================
    # STATEMENTS — sharing info
    # =========================
    statement_patterns = [
        r"^my\s+",
        r"^i\s+am\s+", r"^i'm\s+",
        r"^i\s+have\s+", r"^i\s+like\s+",
        r"^i\s+love\s+", r"^i\s+hate\s+",
        r"^this\s+is\s+", r"^that\s+is\s+",
    ]
    for pattern in statement_patterns:
        if re.match(pattern, query_lower):
            # But not if it ends with ? (e.g., "my name is?" — rare)
            if not query.strip().endswith("?"):
                return "statement"
    
    # =========================
    # QUESTIONS — asking for info
    # =========================
    question_patterns = [
        r"^who\s+", r"^what\s+", r"^when\s+", r"^where\s+",
        r"^why\s+", r"^how\s+", r"^which\s+", r"^whose\s+",
        r"^is\s+", r"^are\s+", r"^was\s+", r"^were\s+",
        r"^do\s+", r"^does\s+", r"^did\s+",
        r"^can\s+", r"^could\s+", r"^would\s+", r"^should\s+",
        r"^tell\s+me\s+", r"^explain\s+", r"^describe\s+",
        r"^what's\s+", r"^who's\s+", r"^where's\s+",
        r"^how's\s+", r"^when's\s+",
    ]
    for pattern in question_patterns:
        if re.match(pattern, query_lower):
            return "question"
    
    # Ends with question mark
    if query.strip().endswith("?"):
        return "question"
    
    # =========================
    # INFO KEYWORDS — treat as question
    # =========================
    info_keywords = ["weather", "temperature", "news", "price"]
    for keyword in info_keywords:
        if keyword in query_lower:
            return "question"
    
    # =========================
    # DEFAULT — chat (safe fallback for unmatched)
    # =========================
    return "chat"