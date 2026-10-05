import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..access import get_owned_document
from ..database import get_db
from ..deps import get_current_user
from ..models import User, ChatMessage
from ..schemas import ChatIn, ChatOut
from ..embedding_service import embed_texts
from ..vector_service import search_chunks, overview_chunks
from ..llm_service import answer_question, is_summary_request

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger("uvicorn.error")

@router.post("/ask", response_model=ChatOut)
def ask(data: ChatIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = get_owned_document(db, user, data.document_id)
    try:
        q_vec = embed_texts([data.question], task_type="RETRIEVAL_QUERY")[0]
    except Exception:
        logger.exception("Question embedding failed")
        raise HTTPException(502, "Could not process the question. Check GEMINI_API_KEY and the backend logs.")
    if is_summary_request(data.question):
        chunks = overview_chunks(db, user.id, doc.id, limit=12)
    else:
        chunks = search_chunks(db, user.id, doc.id, q_vec, k=8)
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