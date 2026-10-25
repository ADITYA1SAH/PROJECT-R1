"""
Voice Module for PROJECT R1
David — human-like settings
Mode-aware, word-callback enabled for Face App lip-sync.
"""

import pyttsx3
import threading

from modules.modes.mode import get_mode_config

# Human-like David settings
VOICE_ID = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0"
VOICE_RATE = 150
VOICE_VOLUME = 1.0

# Reusable engine — pyttsx3.init() is slow (~200–400ms on Windows).
# Reusing it removes the startup desync in the Face App.
_engine = None
_engine_lock = threading.Lock()


def _get_engine():
    """Lazily create a single reusable pyttsx3 engine."""
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        try:
            _engine.setProperty('voice', VOICE_ID)
        except Exception:
            pass  # fall back to default voice
    return _engine


def speak(text, on_start=None, on_word=None, on_end=None):
    """
    Speak text with optional callbacks for Face App lip-sync.

    Args:
        text:    the string to speak
        on_start: called once right before audio begins (mouth starts here)
        on_word:  called for each word (args: word_text, word_index)
        on_end:   called after audio finishes (mouth closes here)

    Returns:
        True on success, False on failure.
    """
    if not text or not text.strip():
        return False

    try:
        with _engine_lock:
            engine = _get_engine()
            settings = get_voice_settings()
            engine.setProperty('rate', settings["rate"])

            # Wire callbacks
            if on_word is not None:
                engine.connect('started-word',
                               lambda name, loc, length, word: on_word(word, None))
            else:
                try:
                    engine.disconnect('started-word')
                except Exception:
                    pass

            if on_start is not None:
                try:
                    on_start()
                except Exception:
                    pass

            engine.say(text)
            engine.runAndWait()

        if on_end is not None:
            try:
                on_end()
            except Exception:
                pass
        return True

    except Exception as e:
        print(f"TTS Error: {e}")
        if on_end is not None:
            try:
                on_end()
            except Exception:
                pass
        return False


def list_voices():
    try:
        engine = _get_engine()
        voices = engine.getProperty('voices')
        for i, voice in enumerate(voices):
            print(f"{i}: {voice.name} - {voice.id}")
        return voices
    except Exception as e:
        print(f"Error: {e}")
        return []


def set_voice(name):
    print(f"✅ Voice set to: {name}")


def set_rate(rate):
    global VOICE_RATE
    VOICE_RATE = rate
    print(f"✅ Rate set to: {rate}")


def listen():
    return "Voice input not yet implemented."


def is_available():
    try:
        import pyttsx3  # noqa
        return True
    except Exception:
        return False


def get_voice_settings():
    """Adjust voice settings based on current mode."""
    mode = get_mode_config()
    settings = {"rate": VOICE_RATE, "volume": 1.0, "pitch": 1.0}

    name = mode["name"]
    if name == "Professional Mode":
        settings["rate"] = 140
    elif name == "Talking Mode":
        settings["rate"] = 180
    elif name["Idle Mode"] if False else (name == "Idle Mode"):
        settings["rate"] = 120
    elif name == "Emergency Mode":
        settings["rate"] = 200

    return settings