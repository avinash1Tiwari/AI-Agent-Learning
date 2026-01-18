from google import genai
import os

# Set your Gemini API key directly in code (for testing)
# os.environ["GEMINI_API_KEY"] = ""  # <-- replace with your real key

# Create Gemini client
client = genai.Client()

# Example texts
texts = [
    "Namaste! Yeh ek test hai.",
    "Machine learning bohot interesting hai!"
]

# Generate embeddings
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=texts
)

# Print embeddings
for i, emb in enumerate(result.embeddings):
    print(f"Text: {texts[i]}")
    print(f"Embedding length: {len(emb)}")
    print("First 5 dims:", emb[:5])
    print("----")
