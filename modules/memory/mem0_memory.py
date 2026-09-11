"""
Mem0 Memory Layer for PROJECT R1
ADD-ONLY — never deletes, never replaces.
Custom instructions enforce friend-like memory behaviour.
"""

from mem0 import Memory

config = {
    "version": "v1.1",
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "raf_memories",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 768,
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "deepseek-coder:6.7b",
            "ollama_base_url": "http://localhost:11434",
            "max_tokens": 2000,
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text:latest",
            "ollama_base_url": "http://localhost:11434",
        }
    },
    "history_db_path": "./data/mem0_history.db",
    "custom_instructions": """
    RAF is a FRIEND, not an assistant. Follow these rules strictly:
    
    MEMORY RULES:
    - NEVER delete any memory. Ever.
    - NEVER replace an old memory with a new one.
    - If a fact changes, ADD the new version alongside the old one.
    - Both versions must remain retrievable.
    - Family memories, personal stories, and important events are PERMANENT.
    - Timestamp every extracted fact.
    - Preserve the full history of changes.
    
    EXTRACTION RULES:
    - Extract names of family members, friends, and important people.
    - Extract personal stories and anecdotes.
    - Extract emotional context.
    - Extract life events (birthdays, milestones, achievements).
    - Extract preferences, even if they change over time.
    - Extract goals, dreams, and values.
    
    Remember: a friend remembers the whole story, not just the latest version.
    """
}

memory = Memory.from_config(config)


def add_memory(messages, user_id="aditya"):
    """Add conversation — Mem0 auto-extracts facts (ADD-ONLY)."""
    return memory.add(messages, user_id=user_id)


def search_memory(query, user_id="aditya", limit=5):
    """Semantic search — finds memories by meaning."""
    return memory.search(query=query, filters={"user_id": user_id}, limit=limit)


def get_all_memories(user_id="aditya"):
    """Get all stored memories."""
    return memory.get_all(filters={"user_id": user_id})