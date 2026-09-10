import json
import requests
import os
import time
from modules.modes.mode import get_mode_config

# Cache for RAF self-questions (static, never change)
RAF_SELF_ANSWERS = {
    "what is your name": "My name is RAF — Revolutionary Artificial Friend.",
    "who are you": "I'm RAF, your revolutionary artificial friend. I'm here to help.",
    "how are you": "I'm doing great! How can I help you?",
    "how are you doing": "I'm doing great! How can I help you?",
    "what are you": "I'm an AI companion named RAF, built to be your friend and assistant.",
    "who created you": "I was created by Aditya, a brilliant developer with a vision.",
    "what can you do": "I can remember facts, search the internet, answer questions, and have conversations with you.",
    "are you connected to the internet": "Yes, I can search the internet when you ask me to.",
}

# Force CPU mode to prevent CUDA crashes
os.environ["OLLAMA_NUM_GPU"] = "0"

OLLAMA_URL = "http://localhost:11434/api/generate"

# Model mapping for each mode
MODEL_MAP = {
    "normal": "phi3:3.8b-mini-4k-instruct-q5_K_M",
    "professional": "deepseek-coder:6.7b",
    "idle": "phi3:3.8b-mini-4k-instruct-q5_K_M",
    "emergency": "phi3:3.8b-mini-4k-instruct-q5_K_M"
}

# Track the current loaded model
_current_model = None


def unload_model():
    """Unload the currently loaded model to free VRAM."""
    global _current_model
    if _current_model:
        try:
            requests.post(
                OLLAMA_URL,
                json={
                    "model": _current_model,
                    "prompt": "",
                    "keep_alive": 0
                },
                timeout=5
            )
            print(f"🔄 Unloaded model: {_current_model}")
            _current_model = None
        except Exception as e:
            print(f"Error unloading model: {e}")


def get_model_for_mode():
    """Get the model name for the current mode."""
    mode = get_mode_config()
    mode_name = mode["name"].lower().replace(" mode", "")
    return MODEL_MAP.get(mode_name, "phi3:3.8b-mini-4k-instruct-q5_K_M")


def generate_response(prompt, timeout=30, user_message=None):
    """
    Generate a response from the LLM.
    Uses RAF_SELF_ANSWERS for self-questions and memory for personal questions.
    """
    # Check RAF self-questions cache
    if user_message:
        msg_lower = user_message.lower().strip()
        for key, answer in RAF_SELF_ANSWERS.items():
            if key in msg_lower:
                return answer
    else:
        prompt_lower = prompt.lower().strip()
        for key, answer in RAF_SELF_ANSWERS.items():
            if key in prompt_lower:
                return answer
    
    # Get the model for the current mode
    model = get_model_for_mode()
    global _current_model
    
    # Unload previous model if different
    if _current_model and _current_model != model:
        unload_model()
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "options": {
                    "num_gpu": 0,
                    "num_ctx": 512
                }
            },
            timeout=timeout
        )
        
        data = response.json()
        if "response" not in data:
            print("OLLAMA ERROR:", data)
            return "I'm having trouble processing that right now."
        
        _current_model = model
        return data["response"].strip()
    
    except requests.Timeout:
        return "I'm still thinking. Let me get back to you."
    except Exception as e:
        print(f"LLM Error: {e}")
        return "I'm having trouble processing that right now."