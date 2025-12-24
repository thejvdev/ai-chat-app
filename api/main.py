from fastapi import FastAPI

from api.auth import router as auth_router
from api.users import router as users_router

from core.db import Base, engine
from models.user import User

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)

Base.metadata.create_all(bind=engine)
