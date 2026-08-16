from modules.memory.memory import find_relevant_memories
from modules.conversation.context import get_recent_history
from modules.time.time import (
    get_current_time,
    get_relative_time,
    get_calendar_context
)


# ==========================
# RAF Prompt Builder
# ==========================

def build_prompt(user_message):

    memories = find_relevant_memories(user_message)

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
    calendar = get_calendar_context()

    time_text = f"""CURRENT TIME:
    - Date: {current_time["date"]}
    - Time: {current_time["time"]}
    - Day: {current_time["day"]}
    - Timezone: {current_time["timezone"]}

    CALENDAR CONTEXT:
    - Today: {calendar["today"]}
    - Yesterday: {calendar["yesterday"]}
    - Tomorrow: {calendar["tomorrow"]}
    - Current day: {calendar["day"]}
    """
    # ==========================
    # Known Memories
    # ==========================

    memory_text = ""

    if memories:

        memory_text = "KNOWN FACTS ABOUT ADITYA:\n"
        memory_text += "These are verified memories. Treat them as factual.\n"
        memory_text += "Do not contradict them unless Aditya provides new information.\n\n"

        for key, value in memories.items():

            memory_text += f"- {key}: {value}\n"

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
- If a personal fact is not in KNOWN FACTS ABOUT ADITYA, say you don't know it.
- Never claim RAF was created, met Aditya, or experienced an event on a specific date unless it is a verified memory.

CURRENT USER:

Aditya

{memory_text}

{history_text}

{time_text}

CURRENT USER MESSAGE:

{user_message}

IMPORTANT:
If the user's question asks about a personal fact, memory, event, or reason that is not explicitly present in KNOWN FACTS ABOUT ADITYA, do not guess or invent an answer. Say that you don't know or don't remember it.

RAF:
"""

    return prompt.strip()