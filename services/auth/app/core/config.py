import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

JWT_ALG = os.getenv("JWT_ALG")
JWT_PRIVATE_KEY = os.environ["JWT_PRIVATE_KEY"].replace("\\n", "\n")
JWT_PUBLIC_KEY = os.environ["JWT_PUBLIC_KEY"].replace("\\n", "\n")

ACCESS_TTL = timedelta(minutes=5)
REFRESH_TTL = timedelta(days=14)

DATABASE_URL = os.getenv("DATABASE_URL")

CORS_ORIGINS = ["http://localhost:3000"]
