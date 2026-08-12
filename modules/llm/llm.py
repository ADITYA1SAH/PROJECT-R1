import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_response(prompt):

    response = requests.post(
    OLLAMA_URL,
    json={
        "model": "qwen3:8b",
        "prompt": prompt,
        "stream": False,
        "think": False
    }
)

    return response.json()["response"].strip()