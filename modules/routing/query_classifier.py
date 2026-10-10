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
    "allow camera ",
)

COMMAND_EXACT = {
    "version", "help", "exit", "quit", "goodbye",
    "show memory", "show session", "show family",
    "show experiences", "show today", "show yesterday",
    "memory maintenance", "clean memory", "export memory",
    # Webcam commands
    "list cameras", "detect cameras", "check new cameras",
    "take photo", "take a photo",
}


# =========================
# CHAT TRIGGERS (exact match)
# =========================
CHAT_EXACT = {
    "hi", "hello", "hey", "yo", "sup", "wassup",
    "hey bro", "hey raf", "hi bro", "hi raf", "hello bro", "hello raf",
    "good morning", "good afternoon", "good evening", "good night",
    "good morning bro", "good afternoon bro", "good evening bro", "good night bro",
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
# PERSONAL PATTERNS (asking about Aditya — must have "my" or "me")
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
    r"\byour\s+favorite\s+thing\b",
    r"\babout\s+being\s+raf\b",
    r"\babout\s+yourself\b",
]


# =========================
# CHAT PATTERNS (opinions, feelings, casual)
# =========================
CHAT_PATTERNS = [
    r"^tell\s+me\s+something\b",         # "tell me something interesting"
    r"^tell\s+me\s+a\s+",                # "tell me a joke"
    r"^do\s+you\s+like\b",               # "do you like talking to me"
    r"^do\s+you\s+think\b",              # "do you think I should..."
    r"^what\s+do\s+you\s+think\b",       # "what do you think about X"
    r"^what\s+makes\s+you\b",            # "what makes you happy"
    r"^what\s+should\s+i\b",             # "what should i do today"
    r"^how\s+do\s+you\s+feel\b",         # "how do you feel about X"
    r"^what\s+would\s+you\b",            # "what would you do"
    r"^can\s+you\s+tell\s+me\s+a\b",     # "can you tell me a story"
    r"^give\s+me\s+advice\b",            # "give me advice"
    r"^i\s+feel\b",                      # "i feel happy"
    r"^i\s+think\b",                     # "i think that..."
    r"^i\s+want\s+to\s+talk\b",          # "i want to talk"
]


# =========================
# WEATHER PATTERNS
# =========================
WEATHER_KEYWORDS = ["weather", "temperature"]


# =========================
# QUESTION PATTERNS
# =========================
QUESTION_STARTERS = [
    r"^who\s+is\b", r"^who\s+was\b", r"^who\s+are\b",
    r"^what\s+is\b", r"^what\s+are\b", r"^what\s+was\b",
    r"^when\s+is\b", r"^when\s+was\b",
    r"^where\s+is\b", r"^where\s+was\b",
    r"^why\s+is\b", r"^why\s+do\b",
    r"^how\s+does\b", r"^how\s+do\b",
    r"^which\s+", r"^whose\s+",
    r"^is\s+", r"^are\s+", r"^was\s+", r"^were\s+",
    r"^does\s+", r"^did\s+",
    r"^can\s+you\s+tell\s+me\s+about\s+",  # "can you tell me about X"
    r"^explain\s+", r"^describe\s+",
    r"^what's\s+", r"^who's\s+", r"^where's\s+",
    r"^how's\s+", r"^when's\s+",
]


def classify_query(query):
    """
    Classify a query into one of 7 types.
    Priority: command → chat → statement → personal → raf_self → weather → question → chat
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
            print(f"🔍 DEBUG: matched command prefix '{prefix}'")
            return "command"
    
    # =========================
    # 2. CHAT (exact match — greetings)
    # =========================
    if q_clean in CHAT_EXACT:
        return "chat"
    
    # =========================
    # 3. CHAT PATTERNS (opinions, feelings, casual questions)
    # =========================
    for pattern in CHAT_PATTERNS:
        if re.match(pattern, q):
            return "chat"
    
    # =========================
    # 4. STATEMENT (sharing info)
    # =========================
    for pattern in STATEMENT_PATTERNS:
        if re.match(pattern, q):
            if not q.endswith("?"):
                return "statement"
    
    # =========================
    # 5. PERSONAL (about Aditya)
    # =========================
    for pattern in PERSONAL_PATTERNS:
        if re.search(pattern, q):
            return "personal"
    
    # =========================
    # 6. RAF SELF (about RAF)
    # =========================
    for pattern in RAF_SELF_PATTERNS:
        if re.search(pattern, q):
            return "raf_self"
    
    # =========================
    # 7. WEATHER
    # =========================
    for keyword in WEATHER_KEYWORDS:
        if keyword in q:
            return "weather"
    
    # =========================
    # 8. QUESTION (factual)
    # =========================
    for pattern in QUESTION_STARTERS:
        if re.match(pattern, q):
            return "question"
    
    if q.endswith("?"):
        return "question"
    
    # =========================
    # 9. DEFAULT → chat
    # =========================
    return "chat"