import os
from dotenv import load_dotenv
import anthropic

# Load .env file
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

client = anthropic.Anthropic(api_key=api_key)

def test_claude():
    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": "Say hello and confirm API is working."
                }
            ]
        )

        print("✅ Claude API is working!")
        print("\nResponse:\n")
        print(response.content[0].text)

    except Exception as e:
        print("❌ Error connecting to Claude API:")
        print(str(e))

if __name__ == "__main__":
    test_claude()


