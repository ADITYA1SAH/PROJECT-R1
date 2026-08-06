"""
R1 Command Router

Future responsibility:
Receive a command and decide which handler should process it.
"""

def route_command(command):
    """
    Temporary router.

    For now it simply returns the command unchanged.
    Future versions will decide which subsystem should handle it.
    """
    return command
# ========= Future =========
#
# - Intent detection
# - Command routing
# - AI routing
# - Permission routing
# - Automation routing
# - Context-aware routing
#