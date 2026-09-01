"""
Internet Search Module for PROJECT R1
Phase 5 — Web search capability
"""

import requests
import json
from modules.llm.llm import generate_response

# Simple cache to avoid repeated searches
_search_cache = {}

# We'll use DuckDuckGo's API (free, no API key required)
SEARCH_URL = "https://api.duckduckgo.com/"

# Simple cache to avoid repeated searches
_search_cache = {}


def search(query):
    """
    Search the web using DuckDuckGo API, then summarize with LLM.
    Returns a short, direct answer.
    """
    # Check cache first
    if query in _search_cache:
        return _search_cache[query]

    try:
        headers = {
            "User-Agent": "PROJECT R1/1.0 (https://github.com/your-repo; aditya@example.com)"
        }

        # First try DuckDuckGo
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=10)
        data = response.json()

        # Extract the answer or summary
        raw_result = None
        if data.get("Abstract"):
            raw_result = data["Abstract"]
        elif data.get("Answer"):
            raw_result = data["Answer"]
        elif data.get("Definition"):
            raw_result = data["Definition"]
        elif data.get("RelatedTopics"):
            for topic in data["RelatedTopics"]:
                if "Text" in topic:
                    raw_result = topic["Text"]
                    break

        # If DuckDuckGo didn't give a clear answer, try Wikipedia
        if not raw_result:
            raw_result = search_wikipedia(query)

        # If we got a result, use LLM to summarize it into 1 sentence
        if raw_result:
            from modules.llm.llm import generate_response
            summary_prompt = f"Answer this question in 1 short sentence (max 15 words): {query}\n\nInformation: {raw_result[:500]}"
            short_answer = generate_response(summary_prompt)
            if short_answer and len(short_answer) < 100:
                _search_cache[query] = short_answer
                return short_answer
            # Fallback: just return the first sentence
            first_sentence = raw_result.split(".")[0] + "."
            _search_cache[query] = first_sentence
            return first_sentence

        # If still no result, return fallback message
        result = f"I searched for '{query}' but couldn't find a clear answer."
        _search_cache[query] = result
        return result

    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        _search_cache[query] = error_msg
        return error_msg


def search_wikipedia(query):
    """
    Fallback search using Wikipedia search API.
    """
    try:
        headers = {
            "User-Agent": "PROJECT R1/1.0 (https://github.com/your-repo; aditya@example.com)"
        }

        # First, search for the best matching page
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 1
        }
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        data = response.json()

        # Get the first search result
        search_results = data.get("query", {}).get("search", [])
        if not search_results:
            return None

        # Get the page title
        page_title = search_results[0]["title"]

        # Now get the summary for that page
        summary_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        response = requests.get(summary_url + page_title.replace(" ", "_"), headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()

            if data.get("extract"):
                # Return only the first sentence (short answer)
                extract = data["extract"]
                # Split by period and take the first sentence
                first_sentence = extract.split(".")[0] + "."
                return first_sentence
            
        return None
    except Exception as e:
        return None


def is_available():
    """Check if internet search is available."""
    try:
        headers = {
            "User-Agent": "PROJECT R1/1.0 (https://github.com/your-repo; aditya@example.com)"
        }
        response = requests.get("https://duckduckgo.com", headers=headers, timeout=3)
        return response.status_code == 200
    except:
        return False