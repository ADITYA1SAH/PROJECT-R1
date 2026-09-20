"""
Query Classifier for PROJECT R1
Determines what type of query the user sent.

Returns one of:
- "command"    → explicit command (show X, mode X, help, exit, version)
- "statement"  → sharing info (my X is Y, I am X, I have X)
- "personal"   → asking about Aditya (my X, about me, do you remember)
- "raf_self"   → asking about RAF (who are you, what can you do)
- "weather"    → weather/temperature
- "question"   → factual (who is X, what is X, when is X)
- "chat"       → greetings + fallback
"""

import re


# =========================
# COMMAND TRIGGERS
# =========================
COMMAND_PREFIXES = (
    "show ", "mode ", "find ", "forget ", "remember ", "export ",
)

COMMAND_EXACT = {
    "version", "help", "exit", "quit", "goodbye",
    "show memory", "show session", "show family",
    "show experiences", "show today", "show yesterday",
    "memory maintenance", "clean memory", "export memory",
}


# =========================
# CHAT TRIGGERS (exact match)
# =========================
CHAT_EXACT = {
    "hi", "hello", "hey", "yo", "sup", "wassup",
    "good morning", "good afternoon", "good evening", "good night",
    "thanks", "thank you", "ty", "ok", "okay", "cool", "nice",
    "lol", "haha", "bye", "goodbye", "see you",
}


# =========================
# STATEMENT PATTERNS
# =========================
STATEMENT_PATTERNS = [
    r"^my\s+\w+\s+is\s+",                  # "my name is X"
    r"^my\s+\w+\s+are\s+",                 # "my hobbies are X"
    r"^my\s+\w+\s+\w+\s+is\s+",            # "my friend Rahul is X"
    r"^my\s+\w+\s+\w+\s+are\s+",           # "my friends Rahul and Priya are X"
    r"^my\s+\w+\s+\w+\s+loves?\s+",        # "my friend Rohan loves gaming"
    r"^my\s+\w+\s+\w+\s+likes?\s+",        # "my friend Priya likes music"
    r"^i\s+am\s+",
    r"^i'm\s+",
    r"^i\s+have\s+",
    r"^i\s+like\s+",
    r"^i\s+love\s+",
    r"^i\s+hate\s+",
    r"^i\s+want\s+",
    r"^remember\s+",
    r"^note\s+",
    r"^save\s+",
    r"^this\s+is\s+",
    r"^that\s+is\s+",
]


# =========================
# PERSONAL PATTERNS (asking about Aditya)
# =========================
PERSONAL_PATTERNS = [
    r"\bmy\s+\w+",              # "my name", "my dad", "my school"
    r"\babout\s+me\b",
    r"\bwho\s+am\s+i\b",
    r"\bwhat\s+do\s+you\s+know\s+about\s+me\b",
    r"\btell\s+me\s+about\s+my\b",
    r"\btell\s+me\s+about\s+me\b",
    r"\bdo\s+you\s+remember\s+my\b",
    r"\bdo\s+you\s+remember\s+when\s+i\b",
    r"\bdid\s+i\b",
    r"\bhave\s+i\b",
    r"\bwhen\s+did\s+i\b",
    r"\bwhere\s+did\s+i\b",
    r"\bwhat\s+did\s+i\b",
    r"\bwhy\s+did\s+i\b",
    r"\bwho\s+did\s+i\b",
]


# =========================
# RAF SELF PATTERNS
# =========================
RAF_SELF_PATTERNS = [
    r"\bwho\s+are\s+you\b",
    r"\bwhat\s+are\s+you\b",
    r"\bwhat\s+is\s+your\s+name\b",
    r"\bwhat's\s+your\s+name\b",
    r"\bhow\s+are\s+you\b",
    r"\bhow\s+are\s+you\s+doing\b",
    r"\bwho\s+created\s+you\b",
    r"\bwho\s+made\s+you\b",
    r"\bwhat\s+can\s+you\s+do\b",
    r"\bare\s+you\s+connected\s+to\s+the\s+internet\b",
    r"\bare\s+you\s+online\b",
    r"\bdo\s+you\s+have\s+internet\b",
    r"\bcan\s+you\s+search\s+the\s+web\b",
]


# =========================
# WEATHER PATTERNS
# =========================
WEATHER_KEYWORDS = ["weather", "temperature"]


# =========================
# QUESTION PATTERNS
# =========================
QUESTION_STARTERS = [
    r"^who\s+", r"^what\s+", r"^when\s+", r"^where\s+",
    r"^why\s+", r"^how\s+", r"^which\s+", r"^whose\s+",
    r"^is\s+", r"^are\s+", r"^was\s+", r"^were\s+",
    r"^do\s+", r"^does\s+", r"^did\s+",
    r"^can\s+", r"^could\s+", r"^would\s+", r"^should\s+",
    r"^tell\s+me\s+about\s+",  # "tell me about X" (not "my X")
    r"^explain\s+", r"^describe\s+",
    r"^what's\s+", r"^who's\s+", r"^where's\s+",
    r"^how's\s+", r"^when's\s+",
]


def classify_query(query):
    """
    Classify a query into one of 7 types.
    Priority order: command → chat → statement → personal → raf_self → weather → question → chat
    """
    if not query or not query.strip():
        return "chat"
    
    q = query.lower().strip()
    q_clean = q.rstrip("?!.,").strip()
    
    # =========================
    # 1. COMMAND
    # =========================
    if q in COMMAND_EXACT:
        return "command"
    for prefix in COMMAND_PREFIXES:
        if q.startswith(prefix):
            return "command"
    
    # =========================
    # 2. CHAT (exact match only)
    # =========================
    if q_clean in CHAT_EXACT:
        return "chat"
    
    # =========================
    # 3. STATEMENT (sharing info)
    # =========================
    for pattern in STATEMENT_PATTERNS:
        if re.match(pattern, q):
            # Not a statement if it ends with "?"
            if not q.endswith("?"):
                return "statement"
    
    # =========================
    # 4. PERSONAL (about Aditya)
    # =========================
    for pattern in PERSONAL_PATTERNS:
        if re.search(pattern, q):
            return "personal"
    
    # =========================
    # 5. RAF SELF (about RAF)
    # =========================
    for pattern in RAF_SELF_PATTERNS:
        if re.search(pattern, q):
            return "raf_self"
    
    # =========================
    # 6. WEATHER
    # =========================
    for keyword in WEATHER_KEYWORDS:
        if keyword in q:
            return "weather"
    
    # =========================
    # 7. QUESTION (factual)
    # =========================
    for pattern in QUESTION_STARTERS:
        if re.match(pattern, q):
            return "question"
    
    # Ends with question mark → question
    if q.endswith("?"):
        return "question"
    
    # =========================
    # 8. DEFAULT → chat
    # =========================
    return "chat"