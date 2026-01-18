from openai import OpenAI
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

# create OpenAI client
client = OpenAI(api_key=os.getenv("OPEN_API_SECRETE_KEY"))

# text to embed
text = "Python is a powerful programming language"

# generate embedding
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
)

embedding_vector = response.data[0].embedding

print("Vector length:", len(embedding_vector))
print("First 10 values:", embedding_vector[:10])