from fastapi import HTTPException
from sqlalchemy.orm import Session
from .models import Document, User

def get_owned_document(db: Session, user: User, document_id: int) -> Document:
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == user.id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc