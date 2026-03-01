from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from typing import Literal
from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path
from pydantic import BaseModel
from langsmith.wrappers import wrap_openai

# ---------------- ENV LOADING ----------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

print("Loading .env from:", ENV_PATH)
load_dotenv(dotenv_path=ENV_PATH)

api_key = os.getenv("OPEN_API_SECRETE_KEY")
if not api_key:
    raise ValueError("OPEN_API_SECRETE_KEY not found in .env")

print("KEY LOADED:", api_key[:5] + "****")

client = wrap_openai(OpenAI(api_key=api_key))


# ---------------- STATE ----------------
class State(TypedDict):
    user_message: str
    is_coding_question: bool
    ai_answer: str


# ---------------- SCHEMAS ----------------
class DetectResponse(BaseModel):
    is_coding_ques: bool


class ResultResponse(BaseModel):
    answer: str


# ---------------- NODES ----------------
def detect_query(state: State):
    user_message = state["user_message"]

    SYSTEM_PROMPT = """
    You are an AI that checks if the user's query is related to programming or coding.
    Return JSON only in format:
    {"is_coding_ques": true or false}
    """

    result = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=DetectResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    is_coding = result.choices[0].message.parsed.is_coding_ques
    print("Detected coding query:", is_coding)

    return {
        "user_message": user_message,
        "is_coding_question": is_coding,
        "ai_answer": ""
    }


def route_query(state: State) -> Literal["solve_coding_question", "solve_other_question"]:
    return "solve_coding_question" if state["is_coding_question"] else "solve_other_question"


def solve_coding_question(state: State):
    user_message = state["user_message"]

    SYSTEM_PROMPT = """
    You are an AI assistant whose job is to answer the user's coding related problem.
    Return JSON only in format:
    {"answer": "<your answer>"}
    """

    result = client.beta.chat.completions.parse(
        model="gpt-4.1",
        response_format=ResultResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    ai_answer = result.choices[0].message.parsed.answer
    print("Coding answer:", ai_answer)

    return {
        "user_message": user_message,
        "is_coding_question": state["is_coding_question"],
        "ai_answer": ai_answer
    }


def solve_other_question(state: State):
    user_message = state["user_message"]

    SYSTEM_PROMPT = """
    You are an AI assistant whose job is to chat normally with the user.
    Return JSON only in format:
    {"answer": "<your reply>"}
    """

    result = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=ResultResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    ai_answer = result.choices[0].message.parsed.answer
    print("Chat answer:", ai_answer)

    return {
        "user_message": user_message,
        "is_coding_question": state["is_coding_question"],
        "ai_answer": ai_answer
    }


# ---------------- GRAPH ----------------
graph_builder = StateGraph(State)

graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_other_question", solve_other_question)

graph_builder.add_edge(START, "detect_query")
graph_builder.add_conditional_edges("detect_query", route_query)
graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_other_question", END)

graph = graph_builder.compile()


# ---------------- CALLER ----------------
def call_graph():
    state1 = {
        "user_message": "aur bhai kya haal hai?",
        "is_coding_question": False,
        "ai_answer": ""
    }

    state2 = {
        "user_message": "what is c sharp",
        "is_coding_question": False,
        "ai_answer": ""
    }

    print("\n--- TEST 1 ---")
    result1 = graph.invoke(state1)
    print("Final Result:", result1)

    print("\n--- TEST 2 ---")
    result2 = graph.invoke(state2)
    print("Final Result:", result2)


call_graph()
