from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..access import get_owned_document
from ..database import get_db
from ..deps import get_current_user
from ..models import User, ChatMessage
from ..schemas import ChatOut

router = APIRouter(prefix="/chat", tags=["Chat History"])

@router.get("/history/{document_id}", response_model=list[ChatOut])
def history(document_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = get_owned_document(db, user, document_id)
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id, ChatMessage.document_id == doc.id)
        .order_by(ChatMessage.id.asc())
        .all()
    )