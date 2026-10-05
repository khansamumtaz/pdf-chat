from sqlalchemy.orm import Session
from .models import Chunk

def search_chunks(db: Session, user_id: int, document_id: int, query_embedding: list[float], k: int = 8) -> list[str]:
    rows = (
        db.query(Chunk)
        .filter(Chunk.user_id == user_id, Chunk.document_id == document_id)
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(k)
        .all()
    )
    return [r.content for r in rows]

def overview_chunks(db: Session, user_id: int, document_id: int, limit: int = 12) -> list[str]:
    rows = (
        db.query(Chunk.content)
        .filter(Chunk.user_id == user_id, Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index.asc())
        .all()
    )
    contents = [r[0] for r in rows]
    if len(contents) <= limit:
        return contents
    step = len(contents) / limit
    return [contents[int(i * step)] for i in range(limit)]