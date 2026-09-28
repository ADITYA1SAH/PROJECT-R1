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
    """Search via SearXNG, then use LLM to extract the answer."""
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
        
        # Build context
        context_parts = []
        for i, r in enumerate(results[:num_results], 1):
            title = r.get("title", "").strip()
            content = r.get("content", "").strip()
            if content:
                context_parts.append(f"[{i}] {title}: {content}")
        
        if not context_parts:
            return None
        
        context = "\n".join(context_parts)
        
        # Extract with LLM
        answer = _extract_with_llm(query, context)
        
        # Validate the answer
        if answer and _is_valid_answer(query, answer):
            if len(answer) < 150:
                _search_cache[query] = answer
            return answer
        
        # Fallback: first content sentence
        for r in results[:3]:
            first_content = r.get("content", "").strip()
            if first_content and len(first_content) > 30:
                fallback = first_content.split(".")[0] + "."
                _search_cache[query] = fallback
                return fallback
        
        return None
    
    except Exception as e:
        print(f"⚠️ SearXNG error: {e}")
        return None

def _is_valid_answer(query, answer):
    print(f"🔍 DEBUG is_valid: query='{query}', answer='{answer}'")
    
    if not answer or answer.upper() == "UNKNOWN":
        print("🔍 DEBUG: reject — empty or unknown")
        return False
    if len(answer) > 300:
        print("🔍 DEBUG: reject — too long")
        return False
    if answer.lower().startswith(("the film", "the movie", "the series")):
        print("🔍 DEBUG: reject — film/movie/series")
        return False
    
    if query.lower().startswith("who is"):
        clean = re.sub(r'[^\w\s]', '', answer)
        words = clean.split()
        print(f"🔍 DEBUG: who-is check — clean='{clean}', words={words}, count={len(words)}")
        if len(words) < 4:
            print("🔍 DEBUG: reject — too short for who-is")
            return False
    
    print("🔍 DEBUG: PASSED validation")
    return True

def _is_valid_answer(query, answer):
    """
    Check if the LLM answer is good enough to return.
    Returns True if valid, False if we should try fallback.
    """
    if not answer or answer.upper() == "UNKNOWN":
        return False
    if len(answer) > 300:
        return False
    if answer.lower().startswith(("the film", "the movie", "the series")):
        return False
    
    # For "who is X" — reject answers that are too short (just a name)
    if query.lower().startswith("who is"):
        # Remove punctuation and count words
        clean = re.sub(r'[^\w\s]', '', answer)
        words = clean.split()
        if len(words) < 4:
            return False
    
    return True


def _extract_with_llm(query, context):
    """Use Ollama to extract a clean answer from search results."""
    try:
        prompt = f"""You extract answers from search results. Be brief and accurate.

STRICT RULES:
1. For "who is X" / "who was X": Extract the sentence that IDENTIFIES X. The sentence MUST start with the person's name. Do NOT use "He is..." or "She is...".
2. For "who is the current X": Return ONLY the name.
3. For "what is X": Give a 1-sentence definition.
4. For "what is the capital of X": Return ONLY the city name.
5. For "what is the tallest/largest X": Return ONLY the answer.
6. Do NOT add "According to..." or "The answer is..."
7. If the answer isn't in the results, say "UNKNOWN".

EXAMPLES:

Question: who is elon musk
Answer: Elon Musk is a billionaire entrepreneur and CEO of Tesla, SpaceX, X, and Neuralink.

Question: who is cristiano ronaldo
Answer: Cristiano Ronaldo is a Portuguese professional footballer who plays as a forward.

Question: who is taylor swift
Answer: Taylor Swift is an American singer-songwriter.

Question: who is the prime minister of india
Answer: Narendra Modi

Question: what is the capital of france
Answer: Paris

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
        answer = answer.rstrip(" .") + "." if answer else answer
        
        # Post-process: fix pronoun-starting answers
        name_match = re.search(r'who\s+is\s+(.+?)(?:\?|$)', query.lower())
        if name_match:
            name = name_match.group(1).strip().rstrip("?")
            name = " ".join(w.capitalize() for w in name.split())
            
            first_word = answer.split()[0].lower().rstrip(",") if answer.split() else ""
            
            if first_word in ["he", "she", "they", "it", "his", "her", "him", "them"]:
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