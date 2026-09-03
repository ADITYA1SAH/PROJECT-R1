import sounddevice as sd
import numpy as np
import time
import wave

# Audio settings
SAMPLE_RATE = 16000
DURATION = 5  # seconds

print("Recording for 5 seconds... Speak!")
recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
sd.wait()  # Wait for recording to finish
print("Recording complete!")

# Save to file (optional)
with wave.open("test_recording.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 16-bit
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(recording.tobytes())

print("Saved to test_recording.wav")