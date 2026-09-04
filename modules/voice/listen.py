"""
Voice Input Module for PROJECT R1
Smart mic — listens until you finish speaking (3 seconds of silence)
"""

import sounddevice as sd
import numpy as np
import speech_recognition as sr
import time
import wave
import tempfile
import os


def listen_to_mic(duration=10, sample_rate=16000, silence_threshold=0.01, silence_duration=2):
    """
    Listens until you stop speaking (3 seconds of silence).
    """
    print("🎙️ Listening... (speak now)")
    
    # Record audio in chunks
    chunk_duration = 0.5  # 500ms chunks
    chunks = []
    silence_count = 0
    max_silence_chunks = int(silence_duration / chunk_duration)
    recording = False
    
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32') as stream:
        while True:
            data, overflowed = stream.read(int(sample_rate * chunk_duration))
            volume = np.sqrt(np.mean(data**2))
            
            if volume > silence_threshold:
                if not recording:
                    recording = True
                    print("🎙️ Recording...")
                chunks.append(data.copy())
                silence_count = 0
            elif recording:
                silence_count += 1
                chunks.append(data.copy())
                if silence_count >= max_silence_chunks:
                    print("🛑 Silence detected — processing...")
                    break
            else:
                pass
            
            if len(chunks) > int(duration / chunk_duration):
                print("⏰ Time limit reached — processing...")
                break
    
    if not chunks:
        print("❌ No speech detected.")
        return ""
    
    # Combine all chunks
    recording_data = np.concatenate(chunks, axis=0)
    recording_int16 = (recording_data * 32767).astype(np.int16)
    
    # Save to temporary WAV file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    wf = wave.open(temp_file.name, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sample_rate)
    wf.writeframes(recording_int16.tobytes())
    wf.close()
    time.sleep(0.2)
    
    # Convert speech to text
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(temp_file.name) as source:
            audio = recognizer.record(source)
        
        # Now the file is released — we can safely delete it
        try:
            text = recognizer.recognize_google(audio)
            print(f"✅ You said: {text}")
            return text
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return ""
        except sr.RequestError:
            print("❌ Could not reach Google speech service")
            return ""
    finally:
        # Always clean up the temp file
        try:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
        except PermissionError:
            time.sleep(0.5)
            try:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
            except:
                pass