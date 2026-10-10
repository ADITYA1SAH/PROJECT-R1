"""
Command Handler for PROJECT R1
All exact-match commands live here.
"""

import sys


def handle_command(command):
    """
    Handle all commands. Returns True if handled, False otherwise.
    """
    command = command.strip().lower()


    # =========================
    # WEBCAM COMMANDS
    # =========================
    if command == "list cameras" or command == "detect cameras":
        from modules.vision.webcam import list_cameras, get_camera_info
        cameras = list_cameras()
        if not cameras:
            print("RAF: No cameras detected.")
            return True
        print(f"RAF: Found {len(cameras)} camera(s):")
        for idx in cameras:
            info = get_camera_info(idx)
            if info:
                print(f"   • Camera {idx} — {info['width']}x{info['height']}")
        return True

    if command == "check new cameras":
        from modules.vision.webcam import check_for_new_cameras
        new = check_for_new_cameras()
        if not new:
            print("RAF: No new cameras detected.")
            return True
        print(f"RAF: Found {len(new)} new camera(s): {new}")
        print("RAF: Say 'allow camera 0' to permit one.")
        return True

    if command.startswith("allow camera "):
        parts = command.split()
        if len(parts) == 3 and parts[2].isdigit():
            idx = int(parts[2])
            from modules.vision.webcam import save_permission, is_permitted
            if is_permitted(idx):
                print(f"RAF: Camera {idx} is already permitted.")
            else:
                save_permission(idx)
                print(f"RAF: ✅ Camera {idx} permission granted.")
        else:
            print("RAF: Usage: allow camera 0")
        return True

    if command == "take photo" or command == "take a photo":
        from modules.vision.webcam import capture_frame, list_cameras, is_permitted
        cameras = list_cameras()
        if not cameras:
            print("RAF: No camera available.")
            return True
        idx = cameras[0]
        if not is_permitted(idx):
            print(f"RAF: I need permission first. Say 'allow camera {idx}'.")
            return True
        frame = capture_frame(idx)
        if frame is None:
            print("RAF: Failed to capture frame.")
            return True
        # Save the frame
        import os
        os.makedirs("data/photos", exist_ok=True)
        from datetime import datetime
        filename = f"data/photos/photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        import cv2
        cv2.imwrite(filename, frame)
        print(f"RAF: 📸 Photo saved to {filename}")
        return True

    
    # =========================
    # EXIT
    # =========================
    if command in ["exit", "quit", "goodbye"]:
        print("Goodbye!")
        sys.exit(0)
    
    # =========================
    # HELP
    # =========================
    if command == "help":
        print()
        print("========== RAF Commands ==========")
        print()
        print("Memory:")
        print("  show memory       - Show all memories")
        print("  show family       - Show family memories")
        print("  show experiences  - Show recent experiences")
        print("  show today        - Show today's memories")
        print("  show yesterday    - Show yesterday's memories")
        print("  find <keyword>    - Search memories")
        print("  forget <key>      - Forget a memory")
        print()
        print("Modes:")
        print("  mode normal       - Default friendly mode")
        print("  mode professional - Work mode")
        print("  mode idle         - Minimal interaction")
        print("  mode emergency    - Urgent mode")
        print()
        print("System:")
        print("  version           - Show version info")
        print("  show session      - Show session stats")
        print("  export memory     - Export to Markdown")
        print("  memory maintenance - Clean and export")
        print("  exit              - Quit RAF")
        print()
        return True
    
    # =========================
    # VERSION
    # =========================
    if command == "version":
        from core.handlers.version_handler import handle_version
        handle_version()
        return True
    
    # =========================
    # SHOW SESSION
    # =========================
    if command == "show session":
        from core.handlers.session_handler import handle_show_session
        handle_show_session()
        return True
    
    # =========================
    # SHOW MEMORY
    # =========================
    if command == "show memory":
        from core.handlers.owner_handler import require_owner
        if require_owner():
            from core.handlers.show_memory_handler import handle_show_memory
            handle_show_memory()
        return True
    
    # =========================
    # SHOW FAMILY
    # =========================
    if command == "show family":
        _show_family()
        return True
    
    # =========================
    # SHOW EXPERIENCES
    # =========================
    if command == "show experiences":
        from modules.memory.experience import get_recent
        print()
        print("========== Recent Experiences ==========")
        for i, exp in enumerate(get_recent(), start=1):
            print(f"{i}. {exp}")
        return True
    
    # =========================
    # SHOW TODAY
    # =========================
    if command == "show today":
        from modules.memory.daily_memory import get_today
        print()
        print("========== Today ==========")
        today = get_today()
        if not today:
            print("No memories from today yet.")
        else:
            for item in today:
                print("-", item)
        return True
    
    # =========================
    # SHOW YESTERDAY
    # =========================
    if command == "show yesterday":
        from modules.memory.daily_memory import get_yesterday
        print()
        print("========== Yesterday ==========")
        yesterday = get_yesterday()
        if not yesterday:
            print("No memories from yesterday.")
        else:
            for item in yesterday:
                print("-", item)
        return True
    
    # =========================
    # MODE SWITCH
    # =========================
    if command.startswith("mode "):
        parts = command.split()
        if len(parts) == 2:
            _switch_mode(parts[1])
        else:
            print("Usage: mode normal | mode professional | mode idle | mode emergency")
        return True
    
    # =========================
    # EXPORT MEMORY
    # =========================
    if command == "export memory":
        from modules.memory.maintenance import export_to_markdown
        export_to_markdown()
        print("✅ Exported to data/exports/MEMORY.md and CONVERSATION.md")
        return True
    
    # =========================
    # MEMORY MAINTENANCE
    # =========================
    if command in ["memory maintenance", "clean memory"]:
        from modules.memory.maintenance import run_maintenance
        run_maintenance()
        return True
    
    # =========================
    # FIND <keyword>
    # =========================
    if command.startswith("find "):
        keyword = command[5:].strip()
        _find_memories(keyword)
        return True
    
    # =========================
    # FORGET <key>
    # =========================
    if command.startswith("forget "):
        from core.handlers.owner_handler import require_owner
        if require_owner():
            from core.handlers.forget_handler import handle_forget
            handle_forget(command)
        return True
    
    # =========================
    # NOT A COMMAND
    # =========================
    return False


# =========================
# HELPERS
# =========================

def _show_family():
    """Display all family memories."""
    from modules.memory.permanent_memory import get_family
    from modules.memory.mem0_memory import search_memory
    
    print()
    print("========== 👨‍👩‍👧 FAMILY MEMORIES ==========")
    print()
    
    permanent = get_family()
    if permanent:
        print("📌 Permanent:")
        for m in permanent:
            print(f"   • {m['fact']}")
    else:
        print("📌 Permanent: No family memories stored yet.")
    
    print()
    
    # Mem0 family search
    try:
        results = search_memory(
            "family mom dad sister brother grandfather grandmother",
            user_id="aditya",
            limit=15
        )
        if isinstance(results, dict):
            results = results.get("results", [])
        if results:
            print("🧠 From Conversation:")
            for r in results:
                if r.get("memory"):
                    print(f"   • {r['memory']}")
        else:
            print("🧠 From Conversation: No memories found.")
    except Exception:
        print("🧠 From Conversation: Search failed.")
    
    print()


def _switch_mode(mode_name):
    """Switch RAF's mode."""
    from modules.modes.mode import set_mode, get_mode_config
    if set_mode(mode_name):
        config = get_mode_config()
        print(f"✅ Mode switched to: {config['name']}")
        print(f"   {config['description']}")
    else:
        print(f"❌ Mode '{mode_name}' not found. Available: normal, professional, idle, emergency")


def _find_memories(keyword):
    """Search experiences + daily memory."""
    from modules.memory.experience import search_experiences
    from modules.memory.daily_memory import search_daily
    
    experiences = search_experiences(keyword)
    daily = search_daily(keyword)
    
    print()
    print(f"========== Search: {keyword} ==========")
    print()
    print(f"Experience Matches : {len(experiences)}")
    print(f"Daily Matches      : {len(daily)}")
    print(f"Total Matches      : {len(experiences) + len(daily)}")
    
    if not experiences and not daily:
        print("No matching memories found.")
        return
    
    if experiences:
        print("\nExperiences:")
        for i, item in enumerate(experiences, start=1):
            print(f"{i}. {item}")
    
    if daily:
        print("\nDaily Journal:")
        for day, item in daily:
            print(f"[{day}] {item}")