from groq import Groq

# Your Groq API key
client = Groq(api_key="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")

print("chatbot(groq streaming): type 'exit', 'quit', 'end', bye, or 'stop' to stope\n the conversation.")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "end", "bye", "stop"]:
        print("Chatbot: Goodbye!")
        break

    print("Chatbot: ", end="", flush=True)
    stream = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "you are a helpful chatbot"},
            {"role": "user", "content": user_input},
        ],
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

    print()