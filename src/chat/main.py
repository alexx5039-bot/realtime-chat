from fastapi import FastAPI
from chat.routes.auth import router as auth_router
from chat.routes.conversation import router as conversation_router
from chat.routes.message import router as message_router

app = FastAPI(title="Real-Time-Chat")

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(conversation_router, prefix="/conversations", tags=["Conversations"])
app.include_router(message_router, prefix="/messages", tags=["Messages"])
