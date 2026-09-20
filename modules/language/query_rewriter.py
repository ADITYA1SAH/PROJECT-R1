"""
Query Rewriter for PROJECT R1
Uses Ollama (Phi-3.5-mini) for typo correction with caching.
Falls back to SymSpell if LLM fails.
"""

import re
import requests
import contractions

# =========================
# Ollama Config
# =========================
OLLAMA_URL = "http://localhost:11434/api/generate"
CORRECTION_MODEL = "phi3:3.8b-mini-4k-instruct-q5_K_M"
LLM_TIMEOUT = 20

# =========================
# Cache
# =========================
CORRECTION_CACHE = {}

# =========================
# Skip LLM for these (exact match)
# =========================
SKIP_LLM_EXACT = {
    "hi", "hello", "hey", "yo", "sup",
    "good morning", "good afternoon", "good evening", "good night",
    "thanks", "thank you", "ok", "okay", "cool", "nice",
    "lol", "haha", "bye", "goodbye",
    "version", "help", "exit", "quit",
    "show memory", "show session", "show family",
    "show experiences", "show today", "show yesterday",
}


# =========================
# Fallback: SymSpell (if LLM fails)
# =========================
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
    """
    Dynamically protect names/cities from memory at runtime.
    """
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
    """
    Use Ollama to fix typos. Returns corrected query or None on failure.
    """
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

Input: who is elon musk
Output: who is elon musk

Input: what is my mom's name
Output: what is my mom's name

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
            # Only take first line
            corrected = corrected.split("\n")[0].strip()
            # Remove prefixes the LLM might add
            for prefix in ["Output:", "output:", "Corrected:", "corrected:"]:
                if corrected.startswith(prefix):
                    corrected = corrected[len(prefix):].strip()
            # Remove quotes
            corrected = corrected.strip('"').strip("'").strip()
            # Remove trailing punctuation
            corrected = corrected.rstrip("?.!,").strip()
            
            # Validate
            if not corrected:
                return None
            if len(corrected) > len(query) * 2:
                return None
            if len(corrected.split()) < len(query.split()) * 0.5:
                return None
            
            return corrected.lower()
    except Exception as e:
        print(f"⚠️ LLM correction failed: {e}")
    
    return None


def fix_with_symspell(query, protected_words):
    """
    Fallback: SymSpell-based typo correction.
    """
    if not SYMSPELL_AVAILABLE:
        return query
    
    words = query.split()
    corrected = []
    
    for word in words:
        # Skip short words, numbers, protected
        if len(word) <= 2 or word.isdigit() or word in protected_words:
            corrected.append(word)
            continue
        
        # Try collapse (heelloo → helo → hello)
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
    Rewrite query:
    1. Expand contractions (fast)
    2. Fix repeated characters (fast)
    3. Try LLM correction
    4. Fallback to SymSpell if LLM fails
    """
    query = query.lower().strip()
    
    if not query:
        return query
    
    # Step 1: Expand contractions
    try:
        query = contractions.fix(query)
    except Exception:
        pass
    
    # Step 2: Fix repeated characters (3+ → 2)
    query = re.sub(r'(.)\1{2,}', r'\1\1', query)
    
    # Step 3: Skip LLM for short commands / greetings
    q_clean = query.rstrip("?!.,").strip()
    if q_clean in SKIP_LLM_EXACT:
        return query
    
    # Step 4: Try LLM
    corrected = fix_with_llm(query)
    if corrected:
        return corrected
    
    # Step 5: Fallback to SymSpell
    protected = get_protected_words()
    return fix_with_symspell(query, protected)