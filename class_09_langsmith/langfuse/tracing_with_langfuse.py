from langfuse.openai import openai
from dotenv import load_dotenv
import os
from pathlib import Path
import json
import requests
from langfuse import observe,Langfuse
import subprocess
import shlex
import platform


# Always load .env from project root explicitly
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

print("Loading .env from:", ENV_PATH)

load_dotenv(dotenv_path=ENV_PATH)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env")

print("KEY LOADED:", api_key[:5] + "****")

SYSTEM_OS = platform.system()
print(SYSTEM_OS)


langfuse = Langfuse()
client = openai.Client(api_key=api_key)


SANDBOX_DIR = os.path.abspath("./sandbox")
os.makedirs(SANDBOX_DIR, exist_ok=True)

# Allowed commands and their allowed arguments pattern
if SYSTEM_OS == "Windows":
    WHITELIST = {
        "dir": {"max_args": 0},
        "echo": {"max_args": 5},
        "whoami": {"max_args": 0},
    }
else:  # Linux / Mac
    WHITELIST = {
        "ls": {"max_args": 1},
        "pwd": {"max_args": 0},
        "whoami": {"max_args": 0},
        "date": {"max_args": 0},
        "echo": {"max_args": 5},
    }

DANGEROUS = {"rm", "mv", "dd", "shutdown", "reboot", "kill", "chmod", "chown", "sudo", "curl", "wget"}

def validate_args(cmd, args):
    for a in args:
        if any(x in a for x in ["..", "/", "~"]):
            return False
        if len(a) > 100:
            return False
    return True




@observe()
def run_command(command: str):
    print("command =>", command)

    try:
        parts = shlex.split(command)
    except Exception:
        return "❌ Invalid command syntax"

    if not parts:
        return "❌ Empty command"

    cmd = parts[0]

    # 🚫 Dangerous commands (global block)
    DANGEROUS = {
        "rm", "del", "mv", "move", "shutdown", "reboot",
        "kill", "taskkill", "chmod", "chown", "sudo",
        "curl", "wget", "scp", "ftp", "dd", "format"
    }

    if cmd.lower() in DANGEROUS:
        return f"❌ '{cmd}' is forbidden"

    try:
        result = subprocess.run(
            parts,                 # full command
            cwd=SANDBOX_DIR,       # 👈 force sandbox
            capture_output=True,
            text=True,
            timeout=5,
            shell=False            # 👈 NO shell = no | && > injection
        )
    except subprocess.TimeoutExpired:
        return "❌ Command timed out"
    except Exception as e:
        return f"❌ Execution failed: {str(e)}"

    return (result.stdout or result.stderr)[:2000]

















@observe()
def get_weather(city):
    # print("🛠 Tool called for:", city)
    # return "31 degree celcius"
    print("🛠 Tool called for:", city)

    # 1️⃣ Get latitude & longitude from city
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_res = requests.get(geo_url).json()

    if "results" not in geo_res:
        return f"City '{city}' not found"

    lat = geo_res["results"][0]["latitude"]
    lon = geo_res["results"][0]["longitude"]

    print(f"📍 Location: {lat}, {lon}")

    # 2️⃣ Call weather API using lat/lon
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current_weather=true"
    )

    weather_res = requests.get(weather_url).json()

    temp = weather_res["current_weather"]["temperature"]

    return f"{temp}°C"

# @observe()
# def run_command(command):
#     print("command is ============> " , command)
#     result = os.system(command=command)
#     return result


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


system_prompt = f"""
    You are a helpful AI Assistant who is specialised in resolving user query.
    You work on start,plan,action,observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relavent tool from the available tools and based on the tool selection you perform an action to complete.
    Wait for the observation and based on the observation from the tool call resolve the user query.

    
    IMPORTANT:
    - The operating system of the machine is: {SYSTEM_OS}
    - You MUST generate shell commands compatible with this OS.
    - Do NOT use commands from other operating systems.
    - The operating system is: {SYSTEM_OS}
    - All commands will run inside a SANDBOX directory.
    - You MUST generate commands compatible with this OS.
    - You MUST NOT access parent directories or absolute paths.
    - You MUST NOT use dangerous commands like rm, mv, shutdown, reboot, chmod, chown, sudo, curl, wget.
    - You MUST NOT use shell features like:
    - >  
    - |  
    - &&  
    - ;  

    Allowed commands:
    - You may use any safe command that does NOT modify system files.
    - All actions happen only inside sandbox.

    File creation rule:
    - To create a file, DO NOT use: echo > file.txt
    - Instead, ALWAYS use:
    python -c "open('filename','w').close()"

    Examples:

    User: create a file named test.txt  
    Action:
    {{
    "step": "action",
    "function": "run_command",
    "input": "python -c \\"open('test.txt','w').close()\\"" 
    }}

    User: list files  
    Windows → dir  
    Linux/Mac → ls  

    Rules:
    - Follow and Output JSON Format.
    - Always perform one step at a time and wait for the next input.
    - Carefully analyse the user query
    - Follow strict JSON format.
    - First plan, then action, then observe, then output.
    - Carefully analyze user query.
    - NEVER invent tools.

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




