
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY not found.")
    raise SystemExit(1)

client = Groq(api_key=api_key)

print("Fetching available Groq models...\n")

try:
    models = client.models.list()
    for model in models.data:
        print(model.id)
except Exception as e:
    print("Error:", e)
