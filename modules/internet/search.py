"""
Internet Search Module for PROJECT R1
Phase 5 — Web search capability
"""

import requests
import json
import re
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

# DuckDuckGo's API (free, no API key required)
SEARCH_URL = "https://api.duckduckgo.com/"


def get_weather(city):
    """Get current weather using wttr.in (free, no API key) — short format."""
    try:
        city = city.strip().replace(" ", "%20")
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return f"Weather in {city.replace('%20', ' ')}: {response.text.strip()}."
        return None
    except:
        return None


def correct_spelling(query):
    """Correct spelling errors using PyEnchant (real dictionary)."""
    if DICT_AVAILABLE:
        words = query.split()
        corrected = []
        for word in words:
            if len(word) > 2:
                if ENGLISH_DICT.check(word):
                    corrected.append(word)
                else:
                    suggestions = ENGLISH_DICT.suggest(word)
                    if suggestions:
                        corrected.append(suggestions[0])
                    else:
                        corrected.append(word)
            else:
                corrected.append(word)
        return " ".join(corrected)
    
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
    
    return query


def search_wikipedia_infobox(query):
    """
    Use Wikipedia API directly to extract infobox data.
    No wptools needed.
    """
    try:
        # Clean the query — remove question words
        clean_query = query.lower()
        for word in ["who is the", "what is the", "where is the", "who is", "what is", "where is", "the"]:
            clean_query = clean_query.replace(word, "")
        clean_query = clean_query.strip()
        
        # Step 1: Search Wikipedia for the best matching page
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": clean_query,
            "format": "json",
            "srlimit": 1
        }
        response = requests.get(search_url, params=params, timeout=10)
        data = response.json()
        
        search_results = data.get("query", {}).get("search", [])
        if not search_results:
            return None
        
        page_title = search_results[0]["title"]
        
        # Step 2: Get the raw wikitext
        params = {
            "action": "parse",
            "page": page_title,
            "prop": "wikitext",
            "format": "json"
        }
        response = requests.get(search_url, params=params, timeout=10)
        data = response.json()
        
        if "parse" not in data:
            return None
        
        wikitext = data["parse"]["wikitext"]["*"]
        
        # Step 3: Extract the incumbent/current field from infobox
        # Look for "incumbent" field
        match = re.search(r'incumbent\s*=\s*\[?\[?([^\|\]\n]+)', wikitext, re.IGNORECASE)
        if match:
            result = match.group(1).strip()
            # Clean up wiki links
            result = re.sub(r'\[\[([^\|\]]+)\|?[^\]]*\]\]', r'\1', result)
            result = re.sub(r'\[\[([^\]]+)\]\]', r'\1', result)
            result = result.strip()
            if result:
                return result
        
        # Look for "current" field
        match = re.search(r'current\s*=\s*\[?\[?([^\|\]\n]+)', wikitext, re.IGNORECASE)
        if match:
            result = match.group(1).strip()
            result = re.sub(r'\[\[([^\|\]]+)\|?[^\]]*\]\]', r'\1', result)
            result = result.strip()
            if result:
                return result
        
        return None
    except Exception as e:
        return None


def search(query):
    """Search the web and return a short, direct answer."""
    # Check cache first
    if query in _search_cache:
        return _search_cache[query]

    # Correct spelling before searching
    query = correct_spelling(query)

    # =========================
    # WEATHER QUERIES
    # =========================
    if "weather" in query.lower() or "temperature" in query.lower():
        city = query.lower()
        for word in ["what is the", "what's the", "whats the", "what is", "whats", "what's"]:
            city = city.replace(word, "")
        for word in ["weather", "temperature", "in", "of", "for", "?"]:
            city = city.replace(word, " ")
        city = " ".join(city.split()).strip()
        if not city:
            city = "London"
        result = get_weather(city)
        if result:
            _search_cache[query] = result
            return result
        else:
            _search_cache[query] = "I couldn't get the weather for that location."
            return _search_cache[query]

    # =========================
    # FACTUAL QUERIES — Try Infobox first
    # =========================
    factual_keywords = ["prime minister", "president", "capital", "current", "incumbent", "chief minister"]
    if any(keyword in query.lower() for keyword in factual_keywords):
        infobox_result = search_wikipedia_infobox(query)
        if infobox_result:
            _search_cache[query] = infobox_result
            return infobox_result

    # =========================
    # CALENDAR / FESTIVAL QUERIES
    # =========================
    if any(keyword in query.lower() for keyword in ["diwali", "holiday", "festival", "when is", "date of"]):
        result = search_duckduckgo(query)
        _search_cache[query] = result
        return result

    # =========================
    # GENERAL KNOWLEDGE — DuckDuckGo HTML first
    # =========================
    try:
        result = search_duckduckgo(query)
        if result and "No results found" not in result and "Search error" not in result:
            _search_cache[query] = result
            return result
    except Exception:
        pass

    # Fallback to DuckDuckGo API
    try:
        headers = {
            "User-Agent": "PROJECT R1/1.0 (https://github.com/your-repo; aditya@example.com)"
        }

        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=5)
        data = response.json()

        raw_result = None
        if data.get("Answer"):
            raw_result = data["Answer"]
        elif data.get("Abstract"):
            raw_result = data["Abstract"]
        elif data.get("Definition"):
            raw_result = data["Definition"]
        elif data.get("RelatedTopics"):
            for topic in data["RelatedTopics"]:
                if "Text" in topic:
                    raw_result = topic["Text"]
                    break

        if not raw_result:
            raw_result = search_wikipedia(query)

        if raw_result:
            if len(raw_result.split(".")) == 1:
                _search_cache[query] = raw_result
                return raw_result
            first_sentence = raw_result.split(".")[0] + "."
            _search_cache[query] = first_sentence
            return first_sentence

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
    """Fallback search using Wikipedia search API."""
    try:
        headers = {
            "User-Agent": "PROJECT R1/1.0 (https://github.com/your-repo; aditya@example.com)"
        }

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

        search_results = data.get("query", {}).get("search", [])
        if not search_results:
            return None

        page_title = search_results[0]["title"]

        summary_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        response = requests.get(summary_url + page_title.replace(" ", "_"), headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()

            if data.get("extract"):
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
    