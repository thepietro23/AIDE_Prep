import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

messages = [
    {
        "role" : "system",
        "content" : "You are a helpful AI Tutor."
    },
    {
        "role" : "user",
        "content" : "Explain Chat Completions in Groq's API."
    }
]

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.7,
    max_tokens=200
)

print(response.choices[0].message.content)