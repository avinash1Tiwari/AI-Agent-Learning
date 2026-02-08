import asyncio
from dotenv import load_dotenv
import os
from pathlib import Path
import platform
import requests

from agents import Agent, Runner, function_tool, set_trace_processors
from langsmith.wrappers import OpenAIAgentsTracingProcessor


# ---------------- ENV LOADING ----------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

print("Loading .env from:", ENV_PATH)
load_dotenv(dotenv_path=ENV_PATH)

api_key = os.getenv("OPEN_API_SECRETE_KEY")
if not api_key:
    raise ValueError("OPEN_API_SECRETE_KEY not found in .env")

print("KEY LOADED:", api_key[:5] + "****")

SYSTEM_OS = platform.system()
print("OS:", SYSTEM_OS)
print("Tracing:", os.getenv("LANGSMITH_TRACING_V2"))
print("Project:", os.getenv("LANGSMITH_PROJECT"))


# ---------------- TOOLS ----------------
@function_tool
def get_weather(city: str) -> str:
    """Takes a city name and returns current temperature."""
    print("🛠 Tool called for:", city)

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_res = requests.get(geo_url).json()

    if "results" not in geo_res:
        return f"City '{city}' not found"

    lat = geo_res["results"][0]["latitude"]
    lon = geo_res["results"][0]["longitude"]

    print(f"📍 Location: {lat}, {lon}")

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current_weather=true"
    )

    weather_res = requests.get(weather_url).json()
    temp = weather_res["current_weather"]["temperature"]

    return f"{temp}°C"


@function_tool
def run_command(command: str) -> str:
    """Runs a shell command on the current OS."""
    print("command is ============>", command)
    return str(os.system(command))


# ---------------- SYSTEM PROMPT ----------------
system_prompt = f"""
You are a helpful AI Assistant who is specialised in resolving user query.
You work on start, plan, action, observe mode.
For the given user query and available tools, plan the step by step execution.

IMPORTANT:
- The operating system of the machine is: {SYSTEM_OS}
- You MUST generate shell commands compatible with this OS.
- Do NOT use commands from other operating systems.

Available Tools:
- get_weather: Takes a city name as an input and return the current weather for the city
- run_command: Takes a shell command as input and executes it on the system
"""


# ---------------- AGENT ----------------
agent = Agent(
    name="System Agent",
    instructions=system_prompt,
    tools=[get_weather, run_command],
)


# ---------------- LANGSMITH TRACING ----------------
set_trace_processors([
    OpenAIAgentsTracingProcessor(project_name=os.getenv("LANGSMITH_PROJECT"))
])



# ---------------- RUN ----------------
async def main():
    query = input("> ")
    result = await Runner.run(agent, query)
    print("\nFINAL OUTPUT:")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
