import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_ALG = os.getenv("JWT_ALG")
JWT_PUBLIC_KEY = os.environ["JWT_PUBLIC_KEY"].replace("\\n", "\n")
