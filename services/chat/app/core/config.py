import os
from dotenv import load_dotenv

load_dotenv()

JWT_ALG = os.getenv("JWT_ALG")
JWT_PUBLIC_KEY = os.environ["JWT_PUBLIC_KEY"].replace("\\n", "\n")

DATABASE_URL = os.getenv("DATABASE_URL")

LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL")
LLM_MODEL = "llama3.1"

CORS_ORIGINS = ["http://localhost:3000"]
