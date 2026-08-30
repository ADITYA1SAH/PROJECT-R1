from modules.grounding.grounding import is_personal_question
from modules.calendar.calendar import is_calendar_question
from modules.emotion.emotion import detect_emotion
from core.handlers.owner_handler import require_owner

"""
Intelligence Router for PROJECT R1
Phase 4.8 — Replaces the giant if/elif chain in brain.py
"""

class IntentRouter:
    def __init__(self, debug=False):
        self.debug = debug
        self.intent_types = {
            "personal": self._is_personal,
            "calendar": self._is_calendar,
            "general": self._is_general,
            "conversation": self._is_conversation
        }

    def route(self, command):
        """
        Returns the intent type for a given command.
        """
        if self._is_command(command):
            if self.debug:
                print(f"🔍 [Router] Command detected: {command}")
            return {"intent": "command"}

        if self._is_personal(command):
            return {"intent": "personal"}

        if self._is_calendar(command):
            return {"intent": "calendar"}

        # Check for emotion
        emotion = detect_emotion(command)
        if emotion != "neutral":
            return {"intent": "emotion", "emotion": emotion}

        return {"intent": "conversation"}

    def _is_personal(self, command):
        return is_personal_question(command)

    def _is_calendar(self, command):
        return is_calendar_question(command)

    def _is_general(self, command):
        # If it's not personal, calendar, or emotion, it's general
        return True

    def _is_command(self, command):
        command_lower = command.lower().strip()
        prefixes = (
            "show ", "find ", "remember ", "forget ",
            "be ", "who am i", "what is", "what did",
            "owner", "friend", "guest", "version",
            "show session", "show experiences",
            "show today", "show yesterday"
        )
        return command_lower.startswith(prefixes)

    def _is_conversation(self, command):
        return True