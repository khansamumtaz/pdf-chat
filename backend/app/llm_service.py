import logging
import re
import time

from google import genai
from google.genai import types

from . import mcp_client
from .config import settings

logger = logging.getLogger("uvicorn.error")

NOT_FOUND = "I could not find this information in the selected document."
PLAIN_TEXT = " Write plain text only. Do not use markdown symbols such as asterisks, hashes or backticks. Use short paragraphs or simple numbered lines."

DEFINE_RE = re.compile(
    r"(what\s+(does|do)\b.+\bmean|\bmeaning\s+of\b|\bdefine\b|\bdefinition\s+of\b)",
    re.IGNORECASE,
)

SUMMARY_RE = re.compile(
    r"(summar|overview|\bgist\b|\bmain\s+points?\b|\bkey\s+points?\b|"
    r"what\s+(is|are)\s+(this|the)\s+(document|pdf|file)\s+about|\babout\s+this\s+(document|pdf|file)\b)",
    re.IGNORECASE,
)

DOC_PROMPT = (
    "You answer questions about a PDF document using ONLY the context provided by the user. "
    "If the answer is not clearly stated in the context, reply with exactly this sentence and nothing else: "
    + NOT_FOUND
    + " Never use outside knowledge and never invent information. Keep answers clear and concise."
)

SUMMARY_PROMPT = (
    "The user wants a summary of a PDF document. The context contains excerpts spread across the whole document. "
    "Summarize the main points using ONLY these excerpts, in a short clear list. Never use outside knowledge. "
    "If the excerpts contain no meaningful content, reply with exactly this sentence and nothing else: "
    + NOT_FOUND
)

WORD_PROMPT = (
    "The user is asking what a word or term means. Call the get_word_definition tool with that word "
    "and answer using its result in one or two clear sentences. "
    "If the tool finds no definition, answer from the PDF context if it covers the term. "
    "If neither has it, reply with exactly this sentence and nothing else: "
    + NOT_FOUND
)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def is_summary_request(question: str) -> bool:
    return bool(SUMMARY_RE.search(question))


def answer_question(question: str, context_chunks: list[str]) -> tuple[str, list[str]]:
    used: list[str] = []

    def get_word_definition(word: str) -> str:
        """Look up the definition of an English or technical word. Use it only when the user asks what a word means."""
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
    wants_definition = bool(DEFINE_RE.search(question))

    if wants_definition:
        system = WORD_PROMPT
    elif is_summary_request(question):
        system = SUMMARY_PROMPT
    else:
        system = DOC_PROMPT

    config = types.GenerateContentConfig(
        system_instruction=system + PLAIN_TEXT,
        temperature=0.2,
        tools=[get_word_definition] if wants_definition else None,
    )

    primary = settings.GEMINI_CHAT_MODEL
    backup = getattr(settings, "GEMINI_FALLBACK_MODEL", "") or primary
    models = [primary, primary, backup, backup, primary]

    last_error = None
    resp = None
    for attempt, model in enumerate(models):
        used.clear()
        try:
            resp = _get_client().models.generate_content(model=model, contents=prompt, config=config)
            break
        except Exception as exc:
            last_error = exc
            logger.warning("Gemini attempt %d (%s) failed: %s", attempt + 1, model, exc)
            if attempt < len(models) - 1:
                time.sleep(2 + attempt)
    if resp is None:
        raise last_error

    text = (resp.text or "").strip()
    return (text or NOT_FOUND), used