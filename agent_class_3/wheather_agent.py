from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path
import json
import platform

# Always load .env from project root explicitly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

print("Loading .env from:", ENV_PATH)

load_dotenv(dotenv_path=ENV_PATH)

api_key = os.getenv("OPEN_API_SECRETE_KEY")

if not api_key:
    raise ValueError("OPEN_API_SECRETE_KEY not found in .env")

print("KEY LOADED:", api_key[:5] + "****")

SYSTEM_OS = platform.system()
print(SYSTEM_OS)

client = OpenAI(api_key=api_key)

def get_weather(city):
    print("🛠 Tool called for:", city)
    return "31 degree celcius"


def run_command(command):
    print("command is ============> " , command)
    result = os.system(command=command)
    return result


available_tools = {
    "get_weather":{
        "fn": get_weather,
        "description": "Takes a city name as an input and return the current weather for the city"
    },
    "run_command":{
        "fn": run_command,
        "description": "Takes the input command from the user and runs it on machine"
    }
}


system_prompt = """
    You are a helpful AI Assistant who is specialised in resolving user query.
    You work on start,plan,action,observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relavent tool from the available tools and based on the tool selection you perform an action to complete.
    Wait for the observation and based on the observation from the tool call resolve the user query.

    
    IMPORTANT:
    - The operating system of the machine is: {SYSTEM_OS}
    - You MUST generate shell commands compatible with this OS.
    - Do NOT use commands from other operating systems.

    Rules:
    - Follow and Output JSON Format.
    - Always perform one step at a time and wait for the next input.
    - Carefully analyse the user query

    Available Tools:
    - get_weather: Takes a city name as an input and return the current weather for the city
    - run_command: Takes a shell command as input and executes it on the system

    Example:
    User Query: What is the weahter of new york?
    Output: {{step:"plan","content":"Alright! The user is interested in weather data of new york"}}
    Output: {{step:"plan","content":"From the available tools, I should call the get_weather"}}
    Output: {{step:"action",function:"get_weather","input" : "new york"}}
    Output: {{step:"observe","output":"15 Deg Celcius"}}
    Output: {{step:"output","content":"The weather of new york seems to be 15 degrees"}}


"""





messages=[
        {"role":"system","content":system_prompt}
    ]


query = input("> ")
messages.append({"role":"user","content":query})


while True:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type":"json_object"},
        messages=messages
    )

    parsed_output = json.loads(response.choices[0].message.content)
    messages.append({"role" : "assistant", "content" : json.dumps(parsed_output) })


    if parsed_output.get("step") == "plan":
        print("parsed-output ==========> ", parsed_output.get("content"))
        continue

    if parsed_output.get("step") == "action":
        tool_name = parsed_output.get("function")
        tool_input = parsed_output.get("input")

        if(available_tools.get(tool_name,False) != False):
            output = available_tools[tool_name].get("fn")(tool_input)
            messages.append({"role" : "assistant", "content" : json.dumps({"step":"observe","output":output}) })

    if parsed_output.get("step") == "output":
        print("parsed-output ==========> ", parsed_output.get("content"))
        break




