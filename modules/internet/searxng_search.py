"""
SearXNG Search for PROJECT R1
Self-hosted, no API key, unlimited queries
"""

import requests
import re

SEARXNG_URL = "http://localhost:8080/search"


def searxng_search(query, num_results=5):
    """
    Search via SearXNG (self-hosted).
    Returns the best answer extracted from results.
    """
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
        # Extract the best answer
        # =========================
        
        # Look for "who is X" questions
        if query.lower().startswith("who is"):
            # Search for the name in the top results
            for result in results[:5]:
                content = result.get("content", "")
                # Look for patterns like "X is the Prime Minister" or "X was sworn-in"
                match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+(?:is|was|has been|became)', content)
                if match:
                    return match.group(1)
        
        # For "what is the capital of X"
        if "capital of" in query.lower():
            for result in results[:3]:
                content = result.get("content", "")
                match = re.search(r'capital\s+(?:is|of)\s+([A-Z][a-z]+)', content)
                if match:
                    return match.group(1)
        
        # For "tallest/largest/biggest X"
        if any(word in query.lower() for word in ["tallest", "largest", "biggest", "highest"]):
            for result in results[:3]:
                content = result.get("content", "")
                # Look for the answer
                match = re.search(r'(?:is|the)\s+([A-Z][a-zA-Z\s]+?)(?:\.|,|\s+located)', content)
                if match:
                    return match.group(1).strip()
        
        # Default: return the first result's content (trimmed)
        first_content = results[0].get("content", "")
        # Take first sentence
        first_sentence = first_content.split(".")[0] + "."
        return first_sentence
    
    except Exception as e:
        return None


def searxng_raw(query, num_results=5):
    """
    Return raw SearXNG results (list of dicts).
    """
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