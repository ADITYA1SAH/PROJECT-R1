"""
Voice Module for PROJECT R1
Using edge-tts + pygame for silent playback
"""

import asyncio
import edge_tts
import platform
import subprocess
import os
import time

# Default voice — change to your favorite
VOICE = "en-AU-WilliamMultilingualNeural"
RATE = "-10%"


def speak(text):
    try:
        output_file = "temp_speech.mp3"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            edge_tts.Communicate(text, VOICE, rate=RATE).save(output_file)
        )
        loop.close()

        # Play the audio using pygame
        play_audio(output_file)

        # Clean up
        if os.path.exists(output_file):
            os.remove(output_file)
        return True

    except Exception as e:
        print(f"TTS Error: {e}")
        return False


def play_audio(file_path):
    """
    Play an MP3 file silently in the background using pygame.
    Falls back to system player if pygame fails.
    """
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        # Wait for the audio to finish
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        
        pygame.mixer.quit()
        
    except Exception as e:
        print(f"Playback Error (pygame): {e}")
        # Fallback to system player
        system = platform.system()
        if system == "Windows":
            os.startfile(file_path)
            time.sleep(1.5)
        elif system == "Darwin":
            subprocess.run(["afplay", file_path])
        else:
            subprocess.run(["aplay", file_path])


def list_voices():
    """
    List all available voices.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        voices = loop.run_until_complete(edge_tts.list_voices())
        loop.close()
        for voice in voices:
            print(f"{voice['Name']} ({voice['Gender']}) - {voice['Locale']}")
        return voices
    except Exception as e:
        print(f"Error listing voices: {e}")
        return []


def set_voice(voice_name):
    global VOICE
    VOICE = voice_name
    print(f"✅ Voice set to: {voice_name}")


def set_rate(rate_percent):
    global RATE
    RATE = rate_percent
    print(f"✅ Rate set to: {rate_percent}")


def listen():
    return "Voice input not yet implemented."


def is_available():
    try:
        import edge_tts
        return True
    except ImportError:
        return False