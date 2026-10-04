from google import genai
from google.genai import types
from .config import settings
from .models import EMBED_DIM

EMBED_MODEL = "gemini-embedding-001"
BATCH = 20
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client

def embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    client = _get_client()
    cfg = types.EmbedContentConfig(task_type=task_type, output_dimensionality=EMBED_DIM)
    vectors = []
    for i in range(0, len(texts), BATCH):
        batch = texts[i:i + BATCH]
        resp = client.models.embed_content(model=EMBED_MODEL, contents=batch, config=cfg)
        vectors.extend([list(e.values) for e in resp.embeddings])
    if len(vectors) != len(texts):
        raise RuntimeError("Embedding count mismatch")
    return vectors