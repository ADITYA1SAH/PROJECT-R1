"""
Internet Search Module for PROJECT R1
Phase 5 — Web search capability
"""

import requests
import json

# We'll use DuckDuckGo's API (free, no API key required)
SEARCH_URL = "https://api.duckduckgo.com/"


def search(query):
    """
    Search the web using DuckDuckGo API.
    Returns a summary of the search results.
    """
    try:
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        response = requests.get(SEARCH_URL, params=params, timeout=10)
        data = response.json()

        # Extract the answer or summary
        if data.get("Abstract"):
            return data["Abstract"]
        elif data.get("Answer"):
            return data["Answer"]
        elif data.get("Definition"):
            return data["Definition"]
        elif data.get("RelatedTopics"):
            for topic in data["RelatedTopics"]:
                if "Text" in topic:
                    return topic["Text"]
        return f"I searched for '{query}' but couldn't find a clear answer."

    except Exception as e:
        return f"Search failed: {str(e)}"


def is_available():
    """Check if internet search is available."""
    try:
        response = requests.get("https://duckduckgo.com", timeout=3)
        return response.status_code == 200
    except:
        return False