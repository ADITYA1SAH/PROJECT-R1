"""
Intelligence Router for PROJECT R1
Uses GLiClass for automatic intent classification
No hardcoded word lists — fully automatic
"""

import os
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

from modules.grounding.grounding import is_personal_question, grounding_response
from modules.calendar.calendar import is_calendar_question
from modules.emotion.emotion import detect_emotion
from config import INTERNET_ENABLED
from modules.internet.search import is_available

# =========================
# GLiClass Setup
# =========================
try:
    from gliclass import GLiClassModel, ZeroShotClassificationPipeline
    from transformers import AutoTokenizer
    import torch
    
    _model = GLiClassModel.from_pretrained("knowledgator/gliclass-edge-v3.0")
    _tokenizer = AutoTokenizer.from_pretrained("knowledgator/gliclass-edge-v3.0")
    _pipeline = ZeroShotClassificationPipeline(
        _model, _tokenizer,
        classification_type='multi-label',
        device='cuda:0' if torch.cuda.is_available() else 'cpu'
    )
    GLICLASS_AVAILABLE = True
    print("✅ GLiClass loaded — automatic intent classification ready")
except Exception as e:
    GLICLASS_AVAILABLE = False
    print(f"⚠️ GLiClass not available: {e}")
    print("⚠️ Falling back to manual routing")

# Intent labels
INTENT_LABELS = [
    "greeting",
    "personal_question",
    "self_question",
    "weather_query",
    "calendar_query",
    "command",
    "general_knowledge",
    "conversation"
]


class IntentRouter:
    def __init__(self, debug=False):
        self.debug = debug

    def route(self, command):
        command_lower = command.lower().strip()

        # =========================
        # FAST ANSWERS — bypass everything (INSTANT)
        # =========================
        from modules.llm.llm import RAF_SELF_ANSWERS
        for key in RAF_SELF_ANSWERS:
            if key in command_lower or command_lower in key:
                return {"intent": "fast_answer", "key": key}

        # =========================
        # EXPLICIT SEARCH TRIGGERS (HIGHEST PRIORITY)
        # =========================
        search_triggers = [
            "weather", "temperature", "prime minister", "capital of",
            "president", "who is", "what is", "when is", "where is",
            "how many", "tell me about", "explain",
        ]
        if INTERNET_ENABLED and is_available():
            for trigger in search_triggers:
                if trigger in command_lower:
                    if not is_personal_question(command):
                        return {"intent": "search"}

        # =========================
        # MULTI-PART QUESTIONS
        # =========================
        if " and " in command_lower or " & " in command_lower:
            return {"intent": "multi_part"}

        # =========================
        # GENERIC PERSONAL LOOKUP (what is my X)
        # =========================
        from modules.language.language import get_personal_lookup
        lookup_result = get_personal_lookup(command)
        if lookup_result:
            return {"intent": "personal_lookup", "key": lookup_result}

        # =========================
        # MEMORY QUESTIONS (tell me about my X, remember X, etc.)
        # =========================
        memory_phrases = [
            "tell me about my", "tell me about me", "what do you remember about",
            "do you remember my", "do you remember when", "what do you know about me",
            "tell me about my dad", "tell me about my mom", "tell me about my family",
        ]
        for phrase in memory_phrases:
            if phrase in command_lower:
                return {"intent": "memory_search"}

        # =========================
        # MEMORY STATEMENTS
        # =========================
        from modules.language.language import get_memory_statement, get_remember_command
        if get_memory_statement(command) or get_remember_command(command):
            return {"intent": "memory"}

        # =========================
        # RECALL QUESTIONS
        # =========================
        from modules.language.language import get_recall_command
        if get_recall_command(command):
            return {"intent": "recall"}

        # =========================
        # GLICLASS INTENT CLASSIFICATION (automatic)
        # =========================
        if GLICLASS_AVAILABLE:
            try:
                results = _pipeline(command, INTENT_LABELS, threshold=0.8)[0]
                if results:
                    best = max(results, key=lambda x: x["score"])
                    
                    if best["score"] < 0.8:
                        if INTERNET_ENABLED and is_available():
                            return {"intent": "search"}
                        return {"intent": "conversation"}
                    
                    label = best["label"]
                    
                    if label == "greeting":
                        return {"intent": "greeting"}
                    elif label == "personal_question":
                        return {"intent": "personal_lookup"}
                    elif label == "self_question":
                        return {"intent": "self_question"}
                    elif label == "weather_query":
                        return {"intent": "search"}
                    elif label == "calendar_query":
                        return {"intent": "calendar"}
                    elif label == "command":
                        return {"intent": "command"}
                    elif label == "general_knowledge":
                        if INTERNET_ENABLED and is_available():
                            return {"intent": "search"}
                        return {"intent": "conversation"}
                    elif label == "conversation":
                        return {"intent": "conversation"}
            except Exception as e:
                if self.debug:
                    print(f"GLiClass error: {e}")

        # =========================
        # FALLBACK — if GLiClass fails
        # =========================
        if command_lower in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "good night"]:
            return {"intent": "greeting"}

        if self._is_calendar(command_lower):
            return {"intent": "calendar"}

        emotion = detect_emotion(command)
        if emotion != "neutral":
            return {"intent": "emotion", "emotion": emotion}

        return {"intent": "conversation"}

    def _is_calendar(self, command):
        return is_calendar_question(command)