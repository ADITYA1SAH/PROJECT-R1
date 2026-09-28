"""
Query Rewriter for PROJECT R1
Uses Ollama (LLM) for typo correction with caching.
Falls back to SymSpell if LLM fails.
"""

import re
import requests
import contractions
import json
import os

CACHE_FILE = "data/rewrite_cache.json"

def _load_disk_cache():
    """Load the rewrite cache from disk."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_disk_cache():
    """Save the rewrite cache to disk."""
    try:
        os.makedirs("data", exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_REWRITE_CACHE, f, indent=2)
    except Exception:
        pass

OLLAMA_URL = "http://localhost:11434/api/generate"
CORRECTION_MODEL = "phi3:3.8b-mini-4k-instruct-q5_K_M"
LLM_TIMEOUT = 20

# Caches
CORRECTION_CACHE = {}                    # LLM result cache
_REWRITE_CACHE = _load_disk_cache()      # Full rewrite cache (persisted to disk)

SKIP_LLM_EXACT = {
    "hi", "hello", "hey", "yo", "sup",
    "good morning", "good afternoon", "good evening", "good night",
    "thanks", "thank you", "ok", "okay", "cool", "nice",
    "lol", "haha", "bye", "goodbye",
    "version", "help", "exit", "quit",
    "show memory", "show session", "show family",
    "show experiences", "show today", "show yesterday",
}


# SymSpell fallback
try:
    from symspellpy import SymSpell, Verbosity
    import os
    sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    dict_path = os.path.join(
        os.path.dirname(__import__('symspellpy').__file__),
        "frequency_dictionary_en_82_765.txt"
    )
    if os.path.exists(dict_path):
        sym_spell.load_dictionary(dict_path, term_index=0, count_index=1)
    SYMSPELL_AVAILABLE = True
except Exception:
    SYMSPELL_AVAILABLE = False


def get_protected_words():
    """Read names/cities from memory at runtime."""
    protected = set()
    try:
        from modules.memory.memory import load_memory
        for key, value in load_memory().items():
            if isinstance(value, str):
                for word in value.lower().split():
                    if len(word) > 2:
                        protected.add(word)
            elif isinstance(value, dict):
                v = value.get("value", "")
                if isinstance(v, str):
                    for word in v.lower().split():
                        if len(word) > 2:
                            protected.add(word)
    except Exception:
        pass
    try:
        from modules.memory.permanent_memory import load_permanent
        for m in load_permanent():
            for word in m["fact"].lower().split():
                if len(word) > 2:
                    protected.add(word)
    except Exception:
        pass
    return protected


def fix_with_llm(query):
    """Use Ollama to fix typos."""
    # Check LLM cache
    if query in CORRECTION_CACHE:
        return CORRECTION_CACHE[query]
    
    try:
        prompt = f"""You are a spelling corrector. Fix typos only. Do NOT change meaning, do NOT add punctuation, do NOT add quotes, do NOT explain.

Examples:
Input: frind rohan
Output: friend rohan

Input: wats my favorite color
Output: what is my favorite color

Input: heelllooo
Output: hello

Input: graviuy
Output: gravity

Input: sho memory
Output: show memory

Input: tell me about my frind rohan
Output: tell me about my friend rohan

Now correct this:
Input: {query}
Output:"""
        
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": CORRECTION_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_gpu": 0,
                    "num_ctx": 512,
                    "temperature": 0.0,
                    "top_p": 0.1,
                    "stop": ["\n", "Input:", "Output:"]
                }
            },
            timeout=LLM_TIMEOUT
        )
        
        data = response.json()
        if "response" in data:
            corrected = data["response"].strip()
            corrected = corrected.split("\n")[0].strip()
            for prefix in ["Output:", "output:", "Corrected:", "corrected:"]:
                if corrected.startswith(prefix):
                    corrected = corrected[len(prefix):].strip()
            corrected = corrected.strip('"').strip("'").strip()
            corrected = corrected.rstrip("?.!,").strip()
            
            if corrected and len(corrected) < len(query) * 2:
                result = corrected.lower()
                CORRECTION_CACHE[query] = result  # Cache LLM result
                return result
    except Exception:
        pass
    return None


def fix_with_symspell(query, protected_words):
    """Fallback: SymSpell-based typo correction."""
    if not SYMSPELL_AVAILABLE:
        return query
    
    words = query.split()
    corrected = []
    for word in words:
        if len(word) <= 2 or word.isdigit() or word in protected_words:
            corrected.append(word)
            continue
        collapsed = re.sub(r'(.)\1+', r'\1', word)
        if sym_spell.words and collapsed in sym_spell.words:
            corrected.append(collapsed)
            continue
        suggestions = sym_spell.lookup(
            word, Verbosity.CLOSEST, max_edit_distance=2, include_unknown=True
        )
        if suggestions:
            corrected.append(suggestions[0].term)
        else:
            corrected.append(word)
    return " ".join(corrected)


def rewrite_query(query):
    """
    Rewrite query with full caching.
    """
    query = query.lower().strip()
    
    if not query:
        return query
    
    # Check full rewrite cache FIRST
    if query in _REWRITE_CACHE:
        return _REWRITE_CACHE[query]
    
    # Step 1: Contractions
    try:
        query = contractions.fix(query)
    except Exception:
        pass
    
    # Step 2: Fix repeated characters
    query = re.sub(r'(.)\1{2,}', r'\1\1', query)
    
    # Step 3: Skip LLM for short commands
    q_clean = query.rstrip("?!.,").strip()
    if q_clean in SKIP_LLM_EXACT:
        _REWRITE_CACHE[query] = query
        _save_disk_cache()
        return query
    
    # Step 4: Skip LLM for very short queries (1-2 words) — use SymSpell
    word_count = len(query.split())
    if word_count <= 2:
        protected = get_protected_words()
        result = fix_with_symspell(query, protected)
        _REWRITE_CACHE[query] = result
        _save_disk_cache()
        return result
    
    # Step 5: Use LLM for 3+ word queries
    corrected = fix_with_llm(query)
    if corrected:
        _REWRITE_CACHE[query] = corrected
        _save_disk_cache()
        return corrected
    
    # Step 6: Fallback to SymSpell
    protected = get_protected_words()
    result = fix_with_symspell(query, protected)
    _REWRITE_CACHE[query] = result
    _save_disk_cache()  # Persist to disk
    return result