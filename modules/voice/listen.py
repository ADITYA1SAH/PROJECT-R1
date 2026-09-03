"""
Voice Input Module for PROJECT R1
Uses sounddevice + SpeechRecognition
"""

import sounddevice as sd
import speech_recognition as sr
import time
import wave
import tempfile
import os


def listen_to_mic(duration=5, sample_rate=16000):
    """
    Listen to microphone for 'duration' seconds and return recognized text.
    """
    print("🎙️ Listening...")
    try:
        # Record audio
        recording = sd.rec(int(duration * sample_rate),
                           samplerate=sample_rate,
                           channels=1,
                           dtype='int16')
        sd.wait()

        # Save to temporary WAV file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(recording.tobytes())

        # Use SpeechRecognition to convert to text
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_file.name) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print(f"✅ You said: {text}")
            
            # Wait and clean up
            time.sleep(0.5)
            try:
                os.unlink(temp_file.name)
            except PermissionError:
                pass  # File will be cleaned up later
            return text

    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return ""
    except sr.RequestError:
        print("❌ Could not reach Google speech service")
        return ""
    except Exception as e:
        print(f"❌ Error: {e}")
        return ""