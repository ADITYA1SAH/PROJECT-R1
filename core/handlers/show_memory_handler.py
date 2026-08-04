from modules.memory.memory import get_all_memory


def handle_show_memory():

    memory = get_all_memory()

    print("\n----- Memory -----")

    for key, value in memory.items():
        print(f"{key} : {value}")