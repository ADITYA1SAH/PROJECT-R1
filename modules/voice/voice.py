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
        engine.setProperty('rate', VOICE_RATE)
        engine.setProperty('voice', VOICE_ID)
        
        # Add slight pauses for natural rhythm
        text = text.replace('.', '. ').replace(',', ', ')
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