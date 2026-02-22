from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient, Limits
from app.core.config import CORS_ORIGINS
from app.api.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = AsyncClient(
        timeout=20,
        limits=Limits(max_connections=50, max_keepalive_connections=10),
    )
    yield
    await app.state.http_client.aclose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=chat_router)
