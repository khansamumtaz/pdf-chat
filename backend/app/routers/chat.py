import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import User, Document, ChatMessage
from ..embedding_service import embed_texts
from ..vector_service import search_chunks
from ..llm_service import answer_question

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger("uvicorn.error")

class ChatIn(BaseModel):
    document_id: int
    question: str = Field(min_length=1, max_length=1000)

class ChatOut(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime
    tools_used: list[str] = []
    model_config = {"from_attributes": True}

def _own_document(db: Session, user: User, document_id: int) -> Document:
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == user.id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc

@router.post("/ask", response_model=ChatOut)
def ask(data: ChatIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = _own_document(db, user, data.document_id)
    try:
        q_vec = embed_texts([data.question], task_type="RETRIEVAL_QUERY")[0]
    except Exception:
        logger.exception("Question embedding failed")
        raise HTTPException(502, "Could not process the question. Check GEMINI_API_KEY and the backend logs.")
    chunks = search_chunks(db, user.id, doc.id, q_vec, k=5)
    try:
        answer, used = answer_question(data.question, chunks)
    except Exception:
        logger.exception("LLM call failed")
        raise HTTPException(502, "The AI model failed to answer. Check the backend logs.")
    msg = ChatMessage(user_id=user.id, document_id=doc.id, question=data.question, answer=answer)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    out = ChatOut.model_validate(msg)
    out.tools_used = used
    return out

@router.get("/history/{document_id}", response_model=list[ChatOut])
def history(document_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = _own_document(db, user, document_id)
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id, ChatMessage.document_id == doc.id)
        .order_by(ChatMessage.id.asc())
        .all()
    )