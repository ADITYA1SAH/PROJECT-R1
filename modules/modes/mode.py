"""
Modes System for PROJECT R1
Defines RAF's behaviour in different situations
"""

MODES = {
    "normal": {
        "name": "Normal Mode",
        "description": "Default friendly companion",
        "personality": "balanced",
        "humor": True,
        "verbosity": "medium",
        "formality": "casual",
        "proactive": True,
        "emoji": True
    },
    "professional": {
        "name": "Professional Mode",
        "description": "Work-focused, no jokes",
        "personality": "serious",
        "humor": False,
        "verbosity": "concise",
        "formality": "formal",
        "proactive": False,
        "emoji": False
    },
    "talking": {
        "name": "Talking Mode",
        "description": "Verbose and chatty",
        "personality": "engaging",
        "humor": True,
        "verbosity": "high",
        "formality": "casual",
        "proactive": True,
        "emoji": True
    },
    "idle": {
        "name": "Idle Mode",
        "description": "Minimal interaction, waits for you",
        "personality": "quiet",
        "humor": False,
        "verbosity": "low",
        "formality": "neutral",
        "proactive": False,
        "emoji": False
    },
    "emergency": {
        "name": "Emergency Mode",
        "description": "Urgent, fast, actionable",
        "personality": "urgent",
        "humor": False,
        "verbosity": "direct",
        "formality": "direct",
        "proactive": True,
        "emoji": False
    }
}

# Current mode
_current_mode = "normal"


def get_mode():
    """Get the current mode."""
    return _current_mode


def set_mode(mode_name):
    """Set the current mode."""
    global _current_mode
    if mode_name in MODES:
        _current_mode = mode_name
        return True
    return False


def get_mode_config():
    """Get the full configuration for the current mode."""
    return MODES.get(_current_mode, MODES["normal"])


def list_modes():
    """List all available modes."""
    return list(MODES.keys())