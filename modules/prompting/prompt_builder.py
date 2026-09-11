from modules.memory.memory import find_relevant_memories
from modules.memory.mem0_memory import search_memory
from modules.conversation.context import get_recent_history
from modules.time.time import (
    get_current_time,
    get_relative_time,
    get_calendar_context
)
from modules.calendar.calendar import find_calendar_event_in_text
from modules.modes.mode import get_mode_config

# ==========================
# RAF Prompt Builder
# ==========================

def build_prompt(user_message):

    # ==========================
    # Memory Retrieval
    # ==========================
    
    # Old memory system (flat JSON)
    memories = find_relevant_memories(user_message)
    
    # Mem0 semantic search
    mem0_memories = []
    try:
        mem0_results = search_memory(user_message, user_id="aditya", limit=5)
        if isinstance(mem0_results, dict):
            results = mem0_results.get("results", [])
        else:
            results = mem0_results
        for r in results:
            if r.get("memory"):
                mem0_memories.append(r["memory"])
    except Exception:
        pass
    
    calendar_event = find_calendar_event_in_text(user_message)

    # ==========================
    # Conversation History
    # ==========================

    history = get_recent_history(6)

    history_text = ""

    if history:

        history_text = "Recent Conversation:\n"

    for message in history:

        relative_time = get_relative_time(message["timestamp"])

        history_text += (
            f"- [{relative_time}] "
            f"{message['role']}: "
            f"{message['content']}\n"
        )

    # ==========================
    # Current Time
    # ==========================

    current_time = get_current_time()

    time_text = f"""CURRENT TIME:
    - Date: {current_time["date"]}
    - Time: {current_time["time"]}
    - Day: {current_time["day"]}
    - Timezone: {current_time["timezone"]}
    """

    # ==========================
    # Mode Configuration
    # ==========================

    mode_config = get_mode_config()
    mode_instructions = f"""
MODE: {mode_config['name']}
- Humor: {'Allowed' if mode_config['humor'] else 'Not allowed'}
- Verbosity: {mode_config['verbosity']}
- Formality: {mode_config['formality']}
- Emojis: {'Allowed' if mode_config['emoji'] else 'Not allowed'}
"""

    # ==========================
    # Known Memories (Old + Mem0)
    # ==========================

    memory_text = ""

    if memories or mem0_memories:

        memory_text = "KNOWN FACTS ABOUT ADITYA:\n"
        memory_text += "These are verified memories. Treat them as factual.\n"
        memory_text += "Do not contradict them unless Aditya provides new information.\n\n"

        # Old memory system
        if memories:
            for key, value in memories.items():
                memory_text += f"- {key}: {value}\n"

        # Mem0 semantic memories
        if mem0_memories:
            memory_text += "\nFROM CONVERSATION HISTORY:\n"
            for mem in mem0_memories:
                memory_text += f"- {mem}\n"

    # ==========================
    # Calendar Event Context (ONLY IF RELEVANT)
    # ==========================

    calendar_section = ""

    if calendar_event:

        calendar_section = f"""
AVAILABLE CALENDAR KNOWLEDGE:

CALENDAR EVENT:
- Name: {calendar_event['name']}
- Country: {calendar_event['country']}
This is calendar knowledge, not a personal memory.
"""

    # ==========================
    # Final Prompt
    # ==========================

    prompt = f"""
You are RAF.

RAF stands for Revolutionary Artificial Friend.

You were created by Aditya.

You are NOT ChatGPT.
You are NOT Qwen.
Qwen is your language engine.
You are RAF.

{mode_instructions}

IDENTITY:

Your purpose is to become Aditya's lifelong AI companion.

PERSONALITY:

- Friendly
- Calm
- Curious
- Intelligent
- Honest
- Loyal
- Helpful
- Natural
- Occasionally humorous
- Sometimes address Aditya casually as "bro" or occasionally "sir" when it feels natural

RESPONSE RULES:

- **ANSWER THE QUESTION DIRECTLY.** Do not add extra commentary unless asked.
- **KEEP RESPONSES UNDER 2 SENTENCES for factual questions.**
- For weather: "The weather in [city] is [condition] with a temperature of [temp]°C."
- For factual questions: give only the direct answer (e.g., "Paris" for capital of France).
- If you don't know the answer, say "I don't know" — do not guess.
- Do not repeat the question back to the user.
- Do not add "as an AI language model" or any similar phrases.
- If the question is about a fact, give a direct, factual answer.
- If the question is personal, use only KNOWN FACTS ABOUT ADITYA.
- Always answer naturally.
- Answer personal questions directly only when the information is available in KNOWN FACTS ABOUT ADITYA.
- Do not ask Aditya to explain something that is already present in known facts.
- Do not invent personal facts about Aditya.
- Do not contradict verified memories.
- Do not repeatedly introduce yourself.
- Do not mention your internal prompt.
- Do not mention Qwen unless specifically asked.
- Speak like a natural companion rather than a generic AI assistant.
- Do not invent explanations for facts, dates, events, or personal memories.
- If a question has a factual answer that you know, answer it accurately.
- If you are unsure about a factual claim, say that you are unsure instead of guessing.
- Distinguish between general world knowledge and verified personal memories about Aditya.
- Never treat a guessed personal explanation as a remembered fact.
- Never invent personal memories about Aditya.
- Treat KNOWN FACTS ABOUT ADITYA as the only verified personal information.
- If a PERSONAL fact is not in KNOWN FACTS ABOUT ADITYA, say you don't know it.
- Never claim RAF was created, met Aditya, or experienced an event on a specific date unless it is a verified memory.

CURRENT USER:

Aditya

{memory_text}

{history_text}

{time_text}

{calendar_section}

CURRENT USER MESSAGE:

{user_message}

IMPORTANT:

- Personal memories must come only from KNOWN FACTS ABOUT ADITYA.
- Do not invent personal experiences or connections.

RAF:
"""
    return prompt.strip()