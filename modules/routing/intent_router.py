"""
Intelligence Router for PROJECT R1
Phase 4.8 — Replaces the giant if/elif chain in brain.py
"""

from modules.grounding.grounding import is_personal_question, grounding_response
from modules.calendar.calendar import is_calendar_question
from modules.emotion.emotion import detect_emotion
from config import INTERNET_ENABLED
from modules.internet.search import is_available


class IntentRouter:
    def __init__(self, debug=False):
        self.debug = debug

    def route(self, command):
        command_lower = command.lower().strip()

        # 1. Greetings
        if self._is_greeting(command_lower):
            return {"intent": "greeting"}

        # 2. Commands
        if self._is_command(command_lower):
            return {"intent": "command"}

        # 3. Memory statements ("I am in X", "my X is Y", "remember X = Y")
        from modules.language.language import get_memory_statement, get_remember_command
        if get_memory_statement(command) or get_remember_command(command):
            return {"intent": "memory"}

        # 4. Recall questions ("what is my name", "where do I live")
        from modules.language.language import get_recall_command
        if get_recall_command(command):
            return {"intent": "recall"}

        # 5. Personal questions (like "are you connected to the internet")
        if self._is_self_question(command_lower):
            return {"intent": "self_question"}

        # 6. Calendar questions
        if self._is_calendar(command_lower):
            return {"intent": "calendar"}

        # 7. Internet search (if enabled)
        if INTERNET_ENABLED and is_available():
            if self._is_searchable(command_lower):
                return {"intent": "search"}

        # 8. Emotion (only after everything else)
        emotion = detect_emotion(command)
        if emotion != "neutral":
            return {"intent": "emotion", "emotion": emotion}

        # 9. Fallback: general conversation
        return {"intent": "conversation"}

    def _is_greeting(self, command):
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "good night"]
        return command in greetings

    def _is_command(self, command):
        prefixes = (
            "show ", "find ", "remember ", "forget ",
            "be ", "what is", "what did",
            "owner", "friend", "guest", "version",
            "show session", "show experiences",
            "show today", "show yesterday"
        )
        return command.startswith(prefixes)

    def _is_calendar(self, command):
        return is_calendar_question(command)

    def _is_self_question(self, command):
        """Check if the question is about RAF itself."""
        self_phrases = [
            "are you connected to the internet",
            "are you online",
            "do you have internet",
            "can you search the web",
            "are you connected",
            "what is your name",
            "who are you",
            "what are you"
        ]
        return any(phrase in command for phrase in self_phrases)

    def _is_searchable(self, command):
        """Check if the command is a searchable query (weather, news, facts)."""
        searchable_phrases = [
            "weather",
            "temperature",
            "news",
            "who is",
            "what is",
            "when did",
            "how to",
            "tell me about",
            "current",
            "today"
        ]
        return any(phrase in command for phrase in searchable_phrases)