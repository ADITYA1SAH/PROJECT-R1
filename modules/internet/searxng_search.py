"""
SearXNG Search for PROJECT R1
Self-hosted, no API key, unlimited queries.
Uses LLM to extract the answer from search results.
"""

import requests
import json
import re

SEARXNG_URL = "http://localhost:8080/search"
OLLAMA_URL = "http://localhost:11434/api/generate"
EXTRACTION_MODEL = "phi3:3.8b-mini-4k-instruct-q5_K_M"

# Cache
_search_cache = {}


def searxng_search(query, num_results=5):
    """
    Search via SearXNG, then use LLM to extract the answer.
    """
    if query in _search_cache:
        return _search_cache[query]
    
    try:
        params = {
            "q": query,
            "format": "json",
            "categories": "general",
            "language": "en",
        }
        response = requests.get(SEARXNG_URL, params=params, timeout=15)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return None
        
        # Build context from top results
        context_parts = []
        for i, r in enumerate(results[:num_results], 1):
            title = r.get("title", "").strip()
            content = r.get("content", "").strip()
            if content:
                context_parts.append(f"[{i}] {title}: {content}")
        
        if not context_parts:
            return None
        
        context = "\n".join(context_parts)
        
        # Extract answer with LLM
        answer = _extract_with_llm(query, context)
        
        if answer:
            if len(answer) < 150:
                _search_cache[query] = answer
            return answer
        
        # Fallback: first content sentence
        first_content = results[0].get("content", "").strip()
        if first_content:
            fallback = first_content.split(".")[0] + "."
            _search_cache[query] = fallback
            return fallback
        
        return None
    
    except Exception as e:
        print(f"⚠️ SearXNG error: {e}")
        return None


def _extract_with_llm(query, context):
    """
    Use Ollama to extract a clean answer from search results.
    """
    try:
        prompt = f"""You extract answers from search results. Be brief and accurate.

STRICT RULES:
1. For "who is X" / "who was X": Extract the sentence that IDENTIFIES X (who they are, what they do). The sentence MUST start with the person's name. Do NOT use "He is..." or "She is..." — always use the full name.
2. For "who is the current X" (prime minister, president, etc.): Return ONLY the name.
3. For "what is X": Give a 1-sentence definition.
4. For "what is the capital of X": Return ONLY the city name.
5. For "what is the tallest/largest/biggest X": Return ONLY the answer.
6. For "when is X": Return ONLY the date.
7. Do NOT add "According to..." or "The answer is..."
8. If the answer isn't in the results, say "UNKNOWN".

EXAMPLES:

Question: who is elon musk
Answer: Elon Musk is a billionaire entrepreneur and CEO of Tesla, SpaceX, X, and Neuralink.

Question: who is the prime minister of india
Answer: Narendra Modi

Question: who is cristiano ronaldo
Answer: Cristiano Ronaldo is a Portuguese professional footballer who plays as a forward.

Question: what is the capital of france
Answer: Paris

Question: what is gravity
Answer: Gravity is a fundamental force that attracts objects toward each other.

Question: who is taylor swift
Answer: Taylor Swift is an American singer-songwriter.

Now:
Question: {query}
Results: {context[:1800]}
Answer:"""
        
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": EXTRACTION_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_gpu": 0,
                    "num_ctx": 2048,
                    "temperature": 0.0
                }
            },
            timeout=45
        )
        
        data = response.json()
        if "response" not in data:
            return None
        
        answer = data["response"].strip()
        answer = answer.split("\n")[0].strip()
        answer = answer.strip('"').strip("'").strip()
        if answer.startswith("Answer:"):
            answer = answer[7:].strip()
        
        # Reject bad answers
        if not answer or answer.upper() == "UNKNOWN":
            return None
        if len(answer) > 300:
            return None
        if answer.lower().startswith(("the film", "the movie", "the series")):
            return None
        
        # =========================
        # POST-PROCESS: Fix pronoun-starting answers
        # =========================
        # Extract the name from query
        name_match = re.search(r'who\s+is\s+(.+?)(?:\?|$)', query.lower())
        if name_match:
            name = name_match.group(1).strip().rstrip("?")
            name = " ".join(w.capitalize() for w in name.split())
            
            # Check if answer starts with a pronoun
            first_word = answer.split()[0].lower().rstrip(",") if answer.split() else ""
            
            if first_word in ["he", "she", "they", "it", "his", "her", "him", "them"]:
                # Replace the pronoun with the name
                # Handle both "He is..." and "He remains..." cases
                rest = " ".join(answer.split()[1:])
                answer = f"{name} {rest}"
        
        return answer
    
    except Exception as e:
        print(f"⚠️ Extraction error: {e}")
        return None


def searxng_raw(query, num_results=5):
    """Return raw SearXNG results."""
    try:
        params = {
            "q": query,
            "format": "json",
            "categories": "general",
            "language": "en",
        }
        response = requests.get(SEARXNG_URL, params=params, timeout=15)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        return data.get("results", [])[:num_results]
    except Exception:
        return []