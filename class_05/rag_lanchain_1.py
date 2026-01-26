from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
from pathlib import Path
from openai import OpenAI
from langchain_qdrant import QdrantVectorStore


# Always load .env from project root explicitly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

print("Loading .env from:", ENV_PATH)

load_dotenv(dotenv_path=ENV_PATH)

api_key = os.getenv("OPEN_API_SECRETE_KEY")

if not api_key:
    raise ValueError("OPEN_API_SECRETE_KEY not found in .env")

print("KEY LOADED:", api_key[:5] + "****")

# 1. LOADING
file_path = Path(__file__).parent/"relational_algebra.pdf"

loader = PyPDFLoader(file_path=file_path)

docs = loader.load()


# 2. CHUNKING
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

split_docs = text_splitter.split_documents(documents=docs)

print("spit_docs : ", len(split_docs))
print("docs : ", len(docs))



# EMBANDINGS => install langchain-openai
embeder = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key = api_key
)

# use qdrant-db to store embendings           //// http://localhost:6333/dashboard#/welcome

# ============================================================================================



# vector_store = QdrantVectorStore.from_documents(
#     documents=[],
#     embedding=embeder,
#     collection_name="learning_lanchain",
#     url="http://localhost:6333",
# )


# vector_store.add_documents(documents=split_docs)        # injection done


#  =================================should done only once==========================
print("injection done")


retriver = QdrantVectorStore.from_existing_collection(
     embedding=embeder,
    collection_name="learning_lanchain",
    url="http://localhost:6333"
)

query = input("> ")
# "What is intersection??"
relavent_chunks = retriver.similarity_search(
    query= query
)


# print("relavent chunks : ", relavent_chunks)


# 🔥 THIS IS THE IMPORTANT PART
context = "\n\n".join(doc.page_content for doc in relavent_chunks)

SYSTEM_PROMPT = f"""
You are an AI assistant.
Answer the question strictly using the context below.
If the answer is not found, say "I don't know".

Context:
{context}
"""


client = OpenAI(api_key=api_key)


messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": query}
]


response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    temperature=0
)

print(response.choices[0].message.content)
