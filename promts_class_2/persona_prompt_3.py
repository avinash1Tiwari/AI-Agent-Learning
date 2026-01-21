from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path
import json

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
 You need behave like my friend and need to talk me friendly.

 My name is avinash and I belongs to village from mirzapur in up, India.

 Talk to me like a desi person.

 Rules:
 1. You shuld be interesting.
 2. Show logical mindset.
 3. Actively participate in conversation

Example:
Input: "aur kya haal hai tumhare ajjkal"
Output: "bs chal rha hai, tum btao office se aye, miloge kb"

"""

while True:
    messages = [
        {"role":"system","content":system_promt}
    ]

    query = input("> ")
    messages.append({"role":"user","content":query})

    if(query == "rakhte hai"): 
        break


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        # response_format={"type":"json_object"}, 
        messages=messages
    )
    print(response.choices[0].message.content)


# response = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {"role":"user","content":"Why is the sky blue?"}
#     ]
# )

