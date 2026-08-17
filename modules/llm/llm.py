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
        },
        timeout=120
    )

    data = response.json()

    if "response" not in data:

        print("\n========== OLLAMA ERROR ==========")
        print("HTTP STATUS:", response.status_code)
        print("RESPONSE:", data)
        print("==================================\n")

        return "I'm having trouble processing that right now."

    return data["response"].strip()