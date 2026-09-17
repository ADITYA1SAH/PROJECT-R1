"""
Query Classifier for PROJECT R1
Distinguishes between: question, statement, chat
"""

import re


def classify_query(query):
    """
    Classify a query as:
    - "question"  → asking for information (needs search/memory)
    - "statement" → sharing information (needs storage)
    - "chat"      → casual conversation (LLM only)
    """
    query_lower = query.lower().strip()
    
    # =========================
    # QUESTION PATTERNS
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
    # STATEMENT PATTERNS (sharing info)
    # =========================
    statement_patterns = [
        r"^my\s+", r"^i\s+am\s+", r"^i'm\s+", r"^i\s+have\s+",
        r"^i\s+like\s+", r"^i\s+love\s+", r"^i\s+hate\s+",
        r"^remember\s+", r"^note\s+", r"^save\s+",
        r"^this\s+is\s+", r"^that\s+is\s+",
    ]
    for pattern in statement_patterns:
        if re.match(pattern, query_lower):
            return "statement"
    
    # =========================
    # CHAT (default for greetings, casual)
    # =========================
    chat_patterns = [
        r"^hi\b", r"^hello\b", r"^hey\b", r"^yo\b",
        r"^good\s+", r"^thanks\b", r"^thank\s+you\b",
        r"^ok\b", r"^okay\b", r"^cool\b", r"^nice\b",
        r"^lol\b", r"^haha\b",
    ]
    for pattern in chat_patterns:
        if re.match(pattern, query_lower):
            return "chat"
    
    # Default: chat (safe fallback)
    return "chat"