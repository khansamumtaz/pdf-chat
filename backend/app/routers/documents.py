import logging
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import User, Document, Chunk, ChatMessage
from ..schemas import DocumentOut, MessageOut
from ..pdf_service import extract_text, chunk_text
from ..embedding_service import embed_texts

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = logging.getLogger("uvicorn.error")
MAX_BYTES = 15 * 1024 * 1024

@router.post("/upload", response_model=DocumentOut, status_code=201)
def upload(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    name = file.filename or "file.pdf"
    data = file.file.read()
    if not name.lower().endswith(".pdf") or not data.startswith(b"%PDF"):
        raise HTTPException(400, "Only valid PDF files are allowed")
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File is larger than 15 MB")
    try:
        text = extract_text(data)
    except Exception:
        raise HTTPException(400, "Could not read this PDF")
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(400, "No text found in this PDF (scanned PDFs are not supported)")
    try:
        vectors = embed_texts(chunks)
    except Exception:
        logger.exception("Embedding failed")
        raise HTTPException(502, "Embedding failed. Check GEMINI_API_KEY and the backend logs.")
    doc = Document(user_id=user.id, filename=name, num_chunks=len(chunks))
    db.add(doc)
    db.flush()
    db.add_all([
        Chunk(document_id=doc.id, user_id=user.id, chunk_index=i, content=c, embedding=v)
        for i, (c, v) in enumerate(zip(chunks, vectors))
    ])
    db.commit()
    db.refresh(doc)
    return doc

@router.get("", response_model=list[DocumentOut])
def list_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.user_id == user.id).order_by(Document.id.desc()).all()

@router.delete("/{doc_id}", response_model=MessageOut)
def delete_document(doc_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == user.id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    db.query(ChatMessage).filter(ChatMessage.document_id == doc.id).delete()
    db.query(Chunk).filter(Chunk.document_id == doc.id).delete()
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted."}