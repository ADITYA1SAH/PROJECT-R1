"""
Query Rewriter for PROJECT R1
Uses SymSpell + TheFuzz for automatic typo correction
No LLM, no hardcoding
"""

import re
import os
import contractions
from symspellpy import SymSpell, Verbosity
from thefuzz import fuzz

# =========================
# LOAD SYMSPELL DICTIONARY
# =========================
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

# Path to the dictionary shipped with symspellpy
dictionary_path = os.path.join(
    os.path.dirname(__import__('symspellpy').__file__),
    "frequency_dictionary_en_82_765.txt"
)

if os.path.exists(dictionary_path):
    sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)


# =========================
# PROTECTED WORDS — never correct
# =========================
PROTECTED_WORDS = {
    "rohan", "priya", "aditya", "rajesh", "sunita", "mohan", "kamla", "arjun",
    "raf", "r1", "noida", "lucknow", "delhi", "mumbai", "kolkata",
    "india", "bharat", "usa", "uk", "japan", "china", "france",
    "python", "javascript", "ollama", "qdrant", "mem0", "searxng", "docker",
    # Both spellings — don't auto-correct one to the other
    "favorite", "favourite",
    "color", "colour",
}


def correct_word(word):
    """
    Correct a single word using SymSpell + TheFuzz.
    Picks the closest match, not just the most frequent.
    """
    # Get top 5 suggestions from SymSpell
    suggestions = sym_spell.lookup(
        word,
        Verbosity.CLOSEST,
        max_edit_distance=2,
        include_unknown=True
    )
    
    if not suggestions:
        return word
    
    # Score each suggestion by fuzz ratio + frequency
    scored = []
    for s in suggestions[:5]:
        similarity = fuzz.ratio(word, s.term)
        # Combine similarity and frequency
        score = (similarity * 0.7) + (min(s.count, 10000) / 10000 * 100 * 0.3)
        scored.append((s.term, similarity, score))
    
    # Pick the best
    best_term, best_similarity, best_score = max(scored, key=lambda x: x[2])
    
    # Only correct if similarity is 70%+
    if best_similarity >= 70:
        return best_term
    
    return word


def rewrite_query(query):
    """
    Automatic query rewriting:
    1. Expand contractions
    2. Fix repeated characters
    3. Correct spelling with SymSpell + TheFuzz
    """
    query = query.lower().strip()
    
    # Step 1: Expand contractions
    try:
        query = contractions.fix(query, slang=True)
    except Exception:
        try:
            query = contractions.fix(query)
        except Exception:
            pass
    
    # Step 2: Fix repeated characters (3+ → 1)
    query = re.sub(r'(.)\1{2,}', r'\1', query)
    
    # Step 3: Spell correction
    words = query.split()
    corrected = []
    
    for word in words:
        # Skip short words, numbers, protected words
        if len(word) <= 2 or word.isdigit() or word in PROTECTED_WORDS:
            corrected.append(word)
            continue
        
        # Try collapsed version first
        collapsed = re.sub(r'(.)\1+', r'\1', word)
        if collapsed != word and collapsed in sym_spell.words:
            corrected.append(collapsed)
            continue
        
        # Otherwise, correct with SymSpell
        corrected.append(correct_word(word))
    
    return " ".join(corrected)