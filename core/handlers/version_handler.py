from modules.system.version import (
    PROJECT,
    VERSION,
    PHASE,
    MODULES
)

def handle_version():

    print()
    print("========== PROJECT INFO ==========")
    print()

    print(f"Project : {PROJECT}")
    print(f"Version : {VERSION}")
    print(f"Current Phase : {PHASE}")

    print()
    print("Modules:")

    for module in MODULES:
        print(f"✓ {module}")

    print()
    print("Status : Ready for Local Intelligence")