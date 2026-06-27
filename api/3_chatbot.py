import os
from groq import Groq
from dotenv import load_dotenv

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

messages = [
    {
        "role" : "system",
        "content" : "You are a helpful assistant that answers questions about Groq's API."
    },
]

print("Welcome to the Groq API Chatbot! Type 'exit' to quit.")

while True:
    user_input = input('You: ')
    if user_input.lower() == 'exit':
        print("Goodbye!")
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.7,
        max_tokens=200
    )

    assistant_reply = response.choices[0].message.content
    print(f"Assistant: {assistant_reply}")

    messages.append({
        "role": "assistant",
        "content": assistant_reply
    })

     