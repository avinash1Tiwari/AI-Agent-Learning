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
 You are an AI Assistant who is expert in breaking down the complex problems and then resolve the user query.

 For a given  user input,analyse the input and break down the problem step by step.
 Atleast think 5-6 steps on ho to solve the problem before solveing it down. 

 
 The steps are you get a user input, you analyse, you think, you again think fro serveral times and then return an output with explaination.

 Follow the steps in sequence that is "analysis", "think", "output", "validate", and finally "result".

 Rules:
 1. Follow the strict json output as per Output schema.
 2. Always perform one step at a time and wait for next input.
 3. Carefully analyse the user query


 Output Format:
 {{step:"string",content:"string"}}

 Example:
 Input: What is 2+3 ?
 Output: {{step:"analyse",content:"Alright! The user is interested in maths query and he asking for a basic airhtematic operation"}}
 Output: {{step:"think",content:"TO perfoem the addition, I must go from left to right and add all the operands"}}
 Output: {{step:"output",content:"4"}}
 Output: {{step:"validate",content:"seems like 4 is correct answer for 2+2"}}
 Output: {{step:"result",content:"2 + 2 = 4 and that is calculated by adding all the numbers"}}


"""
#  client.chat.completions.create
result = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type":"json_object"},
    messages=[
        {"role":"system","content":system_promt},
        {"role":"user","content":"what is 3+5*5"},

        #
        {"role":"assistant", "content": json.dumps({"step":"analyse","content":"The user is asking for a mathematical expression that involves addition and multiplication. I need to determine the correct order of operations (BODMAS/BIDMAS) to solve it."})},
        {"role":"assistant", "content": json.dumps({"step": "think", "content": "According to the order of operations, multiplication should be performed before addition. I will first calculate 5 * 5, and then add 3 to the result."})},
        {"role":"assistant", "content": json.dumps({"step": "validate", "content": "Verifying the result: 5 * 5 equals 25, and adding 3 gives 28, which confirms the calculation is correct."})},
        # {"role":"assistant", "content": json.dumps({"step": "result", "content": "3 + 5 * 5 = 28, calculated by first performing the multiplication (5 * 5 = 25) and then adding 3."})}
    ]

)

print(result.choices[0].message.content)