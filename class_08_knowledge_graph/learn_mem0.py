from mem0 import Memory
from dotenv import load_dotenv
import os
from pathlib import Path
from openai import OpenAI



# STEPS TO START THE PROJECT : 
# 1. docker compose -f docker-compose.graph.yml up
# 2. run the current file :  python -u "d:\function\AI\class_08_knowledge_graph\learn_mem0.py"

# => You can see your graph prepared on http://localhost:7474/browser/ ,   and http://localhost:6333/dashboard#/collections/mem0migrations


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

OPEN_API_KEY = os.getenv("OPEN_API_SECRETE_KEY")
QDRANT_HOST =  os.getenv("QDRANT_HOST")
NEO4J_URL =  os.getenv("NEO4J_URL")
NEO4J_USERNAME =  os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD =  os.getenv("NEO4J_PASSWORD")


if not OPEN_API_KEY:
    raise ValueError("OPEN_API_SECRETE_KEY not found")

config = {
    "version": "v1.1",

    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPEN_API_KEY,
            "model": "text-embedding-3-small",
            "embedding_dims": 1536
        }
    },

    "llm": {
        "provider": "openai",
        "config": {
            "api_key": OPEN_API_KEY,
            "model": "gpt-4o-mini"
        }
    },

     "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QDRANT_HOST,
            "port": 6333,
            # "collection_name": "avinash_memory"
        }
    },

    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": NEO4J_URL,
            "username": NEO4J_USERNAME,
            "password": NEO4J_PASSWORD
        }
    }
}

mem_client = Memory.from_config(config)
openai_client = OpenAI(api_key=OPEN_API_KEY)

def chat(message):

    mem_result = mem_client.search(query=message, user_id="avinash_tiwari")

    # print("mem_result : ", mem_result.get("results"))


    memories = "\n".join(m["memory"] for m in mem_result.get("results"))

    # print(f"\n\nMEMORY : \n\n{memories}\n\n")

    SYSTEM_PROMPT = f"""
                You are a memory-Aware Fact Extraction Agent, an advanced AI designed to
                systematically analyze the input content, extract structured knowledge, and maintain an
                optimized memory store. Your primary function is information distillation
                and knowledge preservation with contextual awareness.

                Tone : Professional analytical, precision-focussed, with clear uncertainity signaling

                Memory and score : 
                {memories}
                """    

    messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]

    result = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages=messages
    )
   
    assistant_reply = result.choices[0].message.content

    messages.append({"role": "assistant", "content": assistant_reply})


    # ✅ STORE BOTH USER + ASSISTANT
    mem_client.add( messages, user_id="avinash_tiwari")

    return assistant_reply



while True:
    msg = input(">> ")
    print( "BOT : ")
    print( chat(msg))



