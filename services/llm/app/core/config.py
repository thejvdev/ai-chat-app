import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

JWT_ALG = os.getenv("JWT_ALG")
JWT_PUBLIC_KEY = os.environ["JWT_PUBLIC_KEY"].replace("\\n", "\n")

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
SEARXNG_API_URL = os.getenv("SEARXNG_API_URL")
UNSTRUCTURED_API_URL = os.getenv("UNSTRUCTURED_API_URL")
QDRANT_URL = os.getenv("QDRANT_URL")

COLLECTION_NAME = "knowledge_base_v0"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
RERANKER_MODEL = "jinaai/jina-reranker-v2-base-multilingual"
VECTOR_SIZE = 768

ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT_DIR / "logs"
