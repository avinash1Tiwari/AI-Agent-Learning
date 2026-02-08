import os
from dotenv import load_dotenv

load_dotenv()  # .env file load karega

print(os.getenv("LANGSMITH_PROJECT"))
