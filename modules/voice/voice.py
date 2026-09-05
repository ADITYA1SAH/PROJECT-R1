"""
Voice Module for PROJECT R1
David — human-like settings
"""

import pyttsx3

# Human-like David settings
VOICE_ID = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
VOICE_RATE = 150  # Slower = more natural
VOICE_VOLUME = 1.0  # Not supported in pyttsx3, but we keep it


def speak(text):
    try:
        engine = pyttsx3.init()
        settings = get_voice_settings()
        engine.setProperty('rate', settings["rate"])
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"TTS Error: {e}")
        return False


def list_voices():
    try:
        engine = pyttsx3.init()
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
        import pyttsx3
        return True
    except:
        return False

from modules.modes.mode import get_mode_config

def get_voice_settings():
    """Adjust voice settings based on current mode."""
    mode = get_mode_config()
    settings = {
        "rate": 150,  # default
        "volume": 1.0,
        "pitch": 1.0
    }
    
    if mode["name"] == "Professional Mode":
        settings["rate"] = 140  # slower, more deliberate
    elif mode["name"] == "Talking Mode":
        settings["rate"] = 180  # faster, more energetic
    elif mode["name"] == "Idle Mode":
        settings["rate"] = 120  # very slow, quiet
    elif mode["name"] == "Emergency Mode":
        settings["rate"] = 200  # fast, urgent
    
    return settings