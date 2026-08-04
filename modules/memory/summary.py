from modules.memory.daily_memory import get_today


def get_daily_summary():

    memories = get_today()

    if not memories:
        return "Nothing important happened today."

    summary = []

    for memory in memories:

        summary.append(f"• {memory}")

    return "\n".join(summary)