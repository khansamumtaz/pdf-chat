from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .database import engine, Base
from . import models  # noqa: F401
from .routers import auth, session, password, users, documents, chat, history

app = FastAPI(title="AI PDF Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def init_db():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(session.router)
app.include_router(password.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(history.router)

@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}