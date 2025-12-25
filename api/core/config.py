import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ALGORITHM = os.getenv("ALGORITHM")
PRIVATE_KEY = os.environ["PRIVATE_KEY"].replace("\\n", "\n")
PUBLIC_KEY = os.environ["PUBLIC_KEY"].replace("\\n", "\n")
