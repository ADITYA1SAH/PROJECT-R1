from modules.llm.llm import generate_response

print("===== RAF Brain Test =====")
print()

while True:

    prompt = input("You: ")

    if prompt.lower() == "exit":
        break

    response = generate_response(prompt)

    print()
    print("RAF:", response)
    print()