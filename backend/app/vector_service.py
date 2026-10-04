from sqlalchemy.orm import Session
from .models import Chunk

def search_chunks(db: Session, user_id: int, document_id: int, query_embedding: list[float], k: int = 5) -> list[str]:
    rows = (
        db.query(Chunk)
        .filter(Chunk.user_id == user_id, Chunk.document_id == document_id)
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(k)
        .all()
    )
    return [r.content for r in rows]