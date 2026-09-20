"""
Weather Handler for PROJECT R1
Handles weather and temperature queries.
Uses wttr.in (free, no API key) — instant and unlimited.
"""

import requests
import re


WTTR_URL = "https://wttr.in/{city}?format=%C+%t"


def handle_weather(command):
    """
    Handle a weather query.
    Returns True if handled, False otherwise.
    """
    command = command.strip().lower()
    
    if not command:
        return False
    
    # Must contain weather-related keyword
    if "weather" not in command and "temperature" not in command:
        return False
    
    # =========================
    # Extract city name
    # =========================
    city = _extract_city(command)
    
    if not city:
        _reply("Which city's weather would you like to know?")
        return True
    
    # =========================
    # Try weather lookup
    # =========================
    result = _get_weather(city)
    
    # =========================
    # Fallback: retry with country hint
    # =========================
    if not result:
        result = _get_weather(f"{city},India")
    
    if result:
        _reply(result)
    else:
        _reply(f"I couldn't get the weather for {city}.")
    
    return True


# =========================
# HELPERS
# =========================

def _extract_city(command):
    """
    Extract the city from a weather query.
    Examples:
    - "what is the weather in noida" → "noida"
    - "weather in new york" → "new york"
    - "what is the temperature in delhi" → "delhi"
    """
    # Remove question words
    cleaned = command
    for phrase in [
        "what is the", "what's the", "whats the",
        "how is the", "how's the", "hows the",
        "tell me the", "tell me",
        "give me the", "give me",
        "weather in", "weather at", "weather for",
        "temperature in", "temperature at", "temperature for",
        "weather", "temperature",
    ]:
        cleaned = cleaned.replace(phrase, " ")
    
    # Remove punctuation
    cleaned = re.sub(r'[?!.,]', '', cleaned)
    
    # Remove standalone "in"
    words = cleaned.split()
    words = [w for w in words if w != "in"]
    
    city = " ".join(words).strip()
    
    return city if city else None


def _get_weather(city):
    """
    Call wttr.in API.
    Returns: "Weather in X: condition +temp°C." or None.
    """
    try:
        city_clean = city.strip()
        if not city_clean:
            return None
        
        encoded = city_clean.replace(" ", "%20").replace(",", "%2C")
        url = f"https://wttr.in/{encoded}?format=%C+%t"
        
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            return None
        
        weather_text = response.text.strip()
        
        # wttr.in returns error text if city not found
        if not weather_text:
            return None
        if "Unknown location" in weather_text:
            return None
        if "Sorry" in weather_text:
            return None
        if len(weather_text) > 100:
            return None
        
        # Clean display city (remove %20, %2C)
        display_city = city_clean.replace(",India", "").replace(",india", "")
        
        return f"Weather in {display_city}: {weather_text}."
    
    except Exception:
        return None


def _reply(response):
    """
    Print response + log to conversation + voice output.
    """
    print("RAF:", response)
    
    try:
        from modules.conversation.context import add_message
        add_message("assistant", response)
    except Exception:
        pass
    
    try:
        from config import VOICE_ENABLED
        if VOICE_ENABLED:
            from modules.voice.voice import speak
            speak(response)
    except Exception:
        pass