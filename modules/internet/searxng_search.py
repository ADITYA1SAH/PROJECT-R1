"""
SearXNG Search for PROJECT R1
Self-hosted, no API key, unlimited queries.
Uses LLM to extract the answer from search results.
"""

import requests
import json

SEARXNG_URL = "http://localhost:8080/search"
OLLAMA_URL = "http://localhost:11434/api/generate"
EXTRACTION_MODEL = "phi3:3.8b-mini-4k-instruct-q5_K_M"

# Cache
_search_cache = {}


def searxng_search(query, num_results=5):
    """
    Search via SearXNG, then use LLM to extract the answer.
    """
    # Check cache
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
        
        # =========================
        # Build context from top results
        # =========================
        context_parts = []
        for i, r in enumerate(results[:num_results], 1):
            title = r.get("title", "").strip()
            content = r.get("content", "").strip()
            if content:
                context_parts.append(f"[{i}] {title}: {content}")
        
        if not context_parts:
            return None
        
        context = "\n".join(context_parts)
        
        # =========================
        # Ask LLM to extract answer
        # =========================
        answer = _extract_with_llm(query, context)
        
        if answer:
            # Only cache short, direct answers (not definitions)
            is_short = len(answer) < 100
            is_definition = answer.lower().startswith(("the ", "a ", "an "))
            if is_short and not is_definition:
                _search_cache[query] = answer
            return answer
        
        # =========================
        # Fallback: first content sentence
        # =========================
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
    Use Ollama to extract a short, direct answer from search results.
    """
    try:
        prompt = f"""You are an answer extractor. Given a question and search results, provide the best short answer.

Rules:
- Keep answers SHORT: 1-2 sentences max
- For "who is X" questions: give a 1-sentence description (who they are)
- For "what is X" questions: give a 1-sentence definition
- For "where is X" or "capital of X": give the location/place
- For "when is X": give the date
- For "who is the current X" (PM, president, etc.): give the NAME only
- Only use information from the search results
- Do NOT add "According to..." or "The answer is..."
- If the results don't contain the answer, say "UNKNOWN"

Examples:
Question: who is the prime minister of india
Results: [1] Narendra Modi is the 14th Prime Minister of India...
Answer: Narendra Modi

Question: who is elon musk
Results: [1] Elon Musk is a billionaire entrepreneur and CEO of Tesla and SpaceX...
Answer: Elon Musk is a billionaire entrepreneur and CEO of Tesla and SpaceX.

Question: what is the capital of france
Results: [1] Paris is the capital of France...
Answer: Paris

Question: what is gravity
Results: [1] Gravity is a fundamental force that attracts objects...
Answer: Gravity is a fundamental force that attracts objects toward each other.

Question: what is the tallest mountain in the world
Results: [1] Mount Everest is the tallest mountain above sea level...
Answer: Mount Everest

Now:
Question: {query}
Results: {context[:1500]}
Answer:"""
        
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": EXTRACTION_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_gpu": 0,
                    "num_ctx": 1024,
                    "temperature": 0.0
                }
            },
            timeout=20
        )
        
        data = response.json()
        if "response" not in data:
            return None
        
        answer = data["response"].strip()
        
        # Clean up
        answer = answer.split("\n")[0].strip()
        answer = answer.strip('"').strip("'").strip()
        if answer.startswith("Answer:"):
            answer = answer[7:].strip()
        
        # Reject bad answers
        if not answer or answer.upper() == "UNKNOWN":
            return None
        if len(answer) > 200:
            return None
        
        return answer
    
    except Exception:
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