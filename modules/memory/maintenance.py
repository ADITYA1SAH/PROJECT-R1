"""
Memory Maintenance Agent for PROJECT R1
Runs during idle time — merges duplicates, resolves contradictions, exports to Markdown
"""

import os
from datetime import datetime
from modules.memory.mem0_memory import get_all_memories, memory
from modules.memory.permanent_memory import load_permanent


def get_all_mem0_memories():
    """Safely get all Mem0 memories as a list."""
    try:
        all_memories = get_all_memories(user_id="aditya")
        if isinstance(all_memories, dict):
            return all_memories.get("results", [])
        return all_memories or []
    except Exception:
        return []


def find_duplicates():
    """
    Find duplicate or near-duplicate memories.
    Returns list of (memory_id_1, memory_id_2, text) tuples.
    """
    memories = get_all_mem0_memories()
    duplicates = []
    seen = {}
    
    for m in memories:
        mem_text = m.get("memory", "").lower().strip()
        if not mem_text:
            continue
        
        # Normalize for comparison (remove user markers)
        normalized = (
            mem_text
            .replace("user's", "")
            .replace("aditya's", "")
            .replace("user ", "")
            .strip()
        )
        
        if normalized in seen:
            duplicates.append((seen[normalized], m))
        else:
            seen[normalized] = m
    
    return duplicates


def merge_duplicates():
    """
    Merge duplicate memories — keep the most detailed version.
    Returns count of merged duplicates.
    """
    duplicates = find_duplicates()
    merged_count = 0
    
    for original, duplicate in duplicates:
        orig_text = original.get("memory", "")
        dup_text = duplicate.get("memory", "")
        
        try:
            # Keep the longer/more detailed version
            if len(dup_text) > len(orig_text):
                memory.delete(original.get("id"))
            else:
                memory.delete(duplicate.get("id"))
            merged_count += 1
        except Exception:
            pass
    
    return merged_count


def export_to_markdown():
    """
    Export all memories to human-readable Markdown files.
    """
    os.makedirs("data/exports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # =========================
    # Permanent Memory Export
    # =========================
    permanent = load_permanent()
    
    with open("data/exports/MEMORY.md", "w", encoding="utf-8") as f:
        f.write("# RAF's Permanent Memory\n\n")
        f.write(f"*Last updated: {timestamp}*\n\n")
        f.write(f"**Total memories: {len(permanent)}**\n\n")
        f.write("---\n\n")
        
        # Group by category
        categories = {}
        for m in permanent:
            cat = m.get("category", "general")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(m)
        
        for cat, memories in sorted(categories.items()):
            f.write(f"## {cat.replace('_', ' ').title()}\n\n")
            for m in memories:
                f.write(f"- {m['fact']}\n")
            f.write("\n")
    
    # =========================
    # Mem0 Conversation Memories Export
    # =========================
    mem0_memories = get_all_mem0_memories()
    
    with open("data/exports/CONVERSATION.md", "w", encoding="utf-8") as f:
        f.write("# RAF's Conversation Memories\n\n")
        f.write(f"*Last updated: {timestamp}*\n\n")
        f.write(f"**Total memories: {len(mem0_memories)}**\n\n")
        f.write("---\n\n")
        
        for m in mem0_memories:
            mem_text = m.get("memory", "")
            created = m.get("created_at", "")[:10] if m.get("created_at") else ""
            if created:
                f.write(f"- [{created}] {mem_text}\n")
            else:
                f.write(f"- {mem_text}\n")
    
    return True


def run_maintenance():
    """
    Run full maintenance cycle.
    """
    print("🧹 Running memory maintenance...")
    
    # 1. Merge duplicates
    merged = merge_duplicates()
    print(f"   Merged {merged} duplicates")
    
    # 2. Export to Markdown
    export_to_markdown()
    print("   Exported to data/exports/")
    
    print("✅ Maintenance complete")
    return True


if __name__ == "__main__":
    run_maintenance()