import json
import requests
import os

# Cache for common questions
CACHE = {}

# Common questions with fast answers
FAST_ANSWERS = {
    "what is your name": "My name is RAF — Revolutionary Artificial Friend.",
    "who are you": "I'm RAF, your revolutionary artificial friend. I'm here to help.",
    "how are you": "I'm doing great! Thanks for asking.",
    "what are you": "I'm an AI companion named RAF, built to be your friend and assistant.",
    "who created you": "I was created by Aditya, a brilliant developer with a vision.",
    "what can you do": "I can remember facts, search the internet, answer questions, and have conversations with you.",
}

# Force CPU mode to prevent CUDA crashes
os.environ["OLLAMA_NUM_GPU"] = "0"

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_response(prompt, stream=False):
    """
    Generate a response from the LLM.
    Uses cache for common questions.
    """
    # Check cache for common questions
    prompt_lower = prompt.lower().strip()
    for key, answer in FAST_ANSWERS.items():
        if key in prompt_lower:
            return answer
    
    # If not in cache, use the LLM
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3:8b",
            "prompt": prompt,
            "stream": False,          # Always non-streaming for now
            "think": False,
            "options": {
                "num_gpu": 0,        # Force CPU mode
                "num_ctx": 2048      # Reduce context size
            }
        },
        timeout=120
    )
    
    data = response.json()
    if "response" not in data:
        print("OLLAMA ERROR:", data)
        return "I'm having trouble processing that right now."
    return data["response"].strip()