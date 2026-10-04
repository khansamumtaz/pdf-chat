import logging

from google import genai
from google.genai import types

from . import mcp_client
from .config import settings

logger = logging.getLogger("uvicorn.error")

NOT_FOUND = "I could not find this information in the selected document."

SYSTEM_PROMPT = (
    "You answer questions about a PDF document. "
    "If the user asks what a word or term means (a definition or meaning), call the get_word_definition tool "
    "and answer using its result. "
    "For every other question, use ONLY the context provided by the user. "
    "If the answer is not clearly stated in the context, reply with exactly this sentence and nothing else: "
    + NOT_FOUND
    + " Never use outside knowledge for those questions and never invent information. "
    "Keep answers clear and concise."
)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def answer_question(question: str, context_chunks: list[str]) -> tuple[str, list[str]]:
    used: list[str] = []

    def get_word_definition(word: str) -> str:
        """Look up the definition of an English or technical word. Use it when the user asks what a word or term means."""
        used.append(word)
        try:
            result = mcp_client.get_word_definition(word)
            logger.info("MCP tool get_word_definition(%r) -> %s", word, result)
            return result
        except Exception:
            logger.exception("MCP call failed")
            return "The dictionary service is currently unavailable."

    context = "\n\n---\n\n".join(context_chunks)
    prompt = "Context from the PDF:\n" + context + "\n\nQuestion: " + question
    resp = _get_client().models.generate_content(
        model=settings.GEMINI_CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
            tools=[get_word_definition],
        ),
    )
    text = (resp.text or "").strip()
    return (text or NOT_FOUND), used