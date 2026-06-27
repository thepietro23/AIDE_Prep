import os 
import json 
from groq import Groq
from dotenv import load_dotenv  

# Configuration

MODEL_NAME = "llama-3.1-8b-instant"

ALLOWED_ERROR_TYPES = [
    "Authentication",
    "Network",
    "Database",
    "Application",
    "System / Resource",
    "Unknown"
]

ALLOWED_SEVERITY_LEVELS = [
    "Low",
    "Medium",       
    "High",
    "Critical"
]

# Client Setup

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def build_prompt(log: str) -> str:
    return f"""
You are an automated error log classification system.

Allowed error_type values:
- Authentication
- Network
- Database
- Application
- System / Resource
- Unknown

Allowed severity values:
- Low
- Medium
- High
- Critical

Rules:
- Respond ONLY in valid JSON
- Do NOT add any extra text
- Use only allowed values
- If unsure, use "Unknown"
- Base severity on potential impact

Return JSON in exactly this format:
{{
  "error_type": "",
  "severity": "",
  "probable_cause": "",
  "recommended_action": ""
}}

Log:
{log}
"""

# Output validation function:

def validate_llm_output(data:dict)->dict:
    if data.get("error_type") not in ALLOWED_ERROR_TYPES:
        data["error_type"] = "Unknown"
    if data.get("severity") not in ALLOWED_SEVERITY_LEVELS:
        data["severity"] = "Unknown"

    return data

# Core classification function:

def classify_error_log(log: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that classifies error logs."},
            {"role": "user", "content": build_prompt(log)}
        ],
        temperature=0.2,
        max_tokens=200,

    )

    raw_output = response.choices[0].message.content

    try:
        parsed_output = json.loads(raw_output)
    except json.JSONDecodeError:
        return {
            "error_type": "Unknown",
            "severity": "Low",
            "probable_cause": "LLM returned invalid JSON",
            "recommended_action": "Inspect raw output and retry"
        }
    
    return validate_llm_output(parsed_output)

# Demo test case:
if __name__ == "__main__":
    sample_log = """
    2024-06-01 12:34:56 ERROR [AuthModule] Failed login attempt for user 'admin' from IP
    """

    result = classify_error_log(sample_log)

    print("\nFINAL CLASSIFICATION RESULT:\n")
    print(json.dumps(result, indent=2))