from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path

# Always load .env from project root explicitly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

print("Loading .env from:", ENV_PATH)

load_dotenv(dotenv_path=ENV_PATH)

api_key = os.getenv("OPEN_API_SECRETE_KEY")

if not api_key:
    raise ValueError("OPEN_API_SECRETE_KEY not found in .env")

print("KEY LOADED:", api_key[:5] + "****")

client = OpenAI(api_key=api_key)

system_promt = """
 You are an AI Assistant who is specialized in maths.
 You should not answer any query which is not related to maths.

 For a given query, help user to solve that along with explaination

 Example:
 Input: 2+3
 Output: 2+3 is 5 which is calculated by adding 2 into 3.

 Input: 3*4
 Output: 3*4 is 12 which is calculted by multiplying 3 by 4.

 Input: Why ice is cold
 Output: Bruh! is it maths related question??
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    # max_tokens=20,
    # temperature=0.5,
    messages=[
         {"role": "system", "content": system_promt},
        {"role":"user","content":"2/6"}
    ]
)

print(response.choices[0].message.content)
