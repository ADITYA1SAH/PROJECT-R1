"""
Internet Search Module for PROJECT R1
Phase 5 — Web search capability
"""

import requests
import json
from modules.llm.llm import generate_response
from modules.internet.browser_search import search_duckduckgo

# Try to use PyEnchant (real dictionary) first
try:
    import enchant
    ENGLISH_DICT = enchant.Dict("en_US")
    DICT_AVAILABLE = True
    print("✅ PyEnchant loaded — using real English dictionary")
except ImportError:
    DICT_AVAILABLE = False
    print("⚠️ PyEnchant not installed. Install with: pip install pyenchant")
    # Fallback to pyspellchecker
    try:
        from spellchecker import SpellChecker
        spell = SpellChecker()
        SPELL_CHECK_AVAILABLE = True
        print("⚠️ Using pyspellchecker as fallback")
    except ImportError:
        SPELL_CHECK_AVAILABLE = False
        print("⚠️ SpellChecker not installed. Install with: pip install pyspellchecker")

# Simple cache to avoid repeated searches
_search_cache = {}

# We'll use DuckDuckGo's API (free, no API key required)
SEARCH_URL = "https://api.duckduckgo.com/"


def get_weather(city):
    """Get current weather using wttr.in (free, no API key) — short format."""
    try:
        city = city.strip().replace(" ", "%20")
        # Use short format: condition + temperature only
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            # Return short weather string (no extra commentary)
            return f"Weather in {city.replace('%20', ' ')}: {response.text.strip()}."
        return None
    except:
        return None


def correct_spelling(query):
    """
    Correct spelling errors using PyEnchant (real dictionary).
    Falls back to pyspellchecker if not available.
    """
    # If using PyEnchant
    if DICT_AVAILABLE:
        words = query.split()
        corrected = []
        for word in words:
            # Only correct words > 2 characters
            if len(word) > 2:
                if ENGLISH_DICT.check(word):
                    corrected.append(word)
                else:
                    suggestions = ENGLISH_DICT.suggest(word)
                    if suggestions:
                        corrected.append(suggestions[0])  # Take the best suggestion
                    else:
                        corrected.append(word)  # Keep original if no suggestion
            else:
                corrected.append(word)
        return " ".join(corrected)
    
    # Fallback to pyspellchecker
    elif SPELL_CHECK_AVAILABLE:
        words = query.split()
        corrected = []
        for word in words:
            if len(word) > 2:
                if word in spell.unknown([word]):
                    correction = spell.correction(word)
                    if correction:
                        corrected.append(correction)
                    else:
                        corrected.append(word)
                else:
                    corrected.append(word)
            else:
                corrected.append(word)
        return " ".join(corrected)
    
    # No spellchecker available
    return query


def search(query):
    """
    Search the web using DuckDuckGo API.
    Returns a short, direct answer.
    """
    # Check cache first
    if query in _search_cache:
        return _search_cache[query]

    # Correct spelling before searching
    query = correct_spelling(query)

    # If it's a weather query, use the weather API (short format)
    if "weather" in query.lower() or "temperature" in query.lower():
        # Extract city name
        city = query.lower().replace("weather", "").replace("temperature", "").replace("in", "").replace("what is the", "").replace("?", "").strip()
        if not city:
            city = "London"
        result = get_weather(city)
        if result:
            _search_cache[query] = result
            return result
        else:
            _search_cache[query] = "I couldn't get the weather for that location."
            return _search_cache[query]

    # For calendar/festival queries, use DuckDuckGo HTML (no blocking)
    if any(keyword in query.lower() for keyword in ["diwali", "holiday", "festival", "when is", "date of"]):
        result = search_duckduckgo(query)
        _search_cache[query] = result
        return result

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
        response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=5)
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

        # If we got a result, return SHORT answer (first sentence only)
        if raw_result:
            # Split by period and take the first sentence
            first_sentence = raw_result.split(".")[0] + "."
            _search_cache[query] = first_sentence
            return first_sentence

        # If no search result, return a clear "I don't know"
        result = f"I searched for '{query}' but couldn't find a clear answer. Try rephrasing your question."
        _search_cache[query] = result
        return result

    except requests.Timeout:
        error_msg = "The search is taking too long. Please try again later."
        _search_cache[query] = error_msg
        return error_msg
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