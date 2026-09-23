from fastapi import FastAPI
from chat.routes.auth import router as auth_router

app = FastAPI(title="Real-Time-Chat")

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
