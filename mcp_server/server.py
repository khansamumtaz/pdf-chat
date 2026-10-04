from urllib.parse import quote

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dictionary", host="0.0.0.0", port=8001)

GLOSSARY = {
    "authentication": "The process of verifying who a user is, for example by checking an email and password or a one-time code.",
    "authorization": "The process of deciding what an already authenticated user is allowed to do or access.",
    "embedding": "A list of numbers that represents the meaning of a piece of text, so similar texts have similar numbers.",
    "vector": "An ordered list of numbers. In AI search, vectors represent the meaning of text and can be compared by distance.",
    "chunk": "A small piece of a larger document, created so each piece can be searched and sent to an AI model separately.",
    "token": "A small signed string that proves who you are. In this app, a JWT access token is sent with every request.",
    "jwt": "JSON Web Token: a signed token that carries a user identity and an expiry time, used to protect APIs.",
    "otp": "One-time password: a short code that works only once and expires quickly, often sent by email.",
    "hashing": "A one-way transformation that turns data such as a password into a fixed fingerprint that cannot be reversed.",
    "api": "Application Programming Interface: a defined way for one program to ask another program to do something.",
    "docker": "A tool that packages an application and everything it needs into containers that run the same on any computer.",
    "container": "A lightweight, isolated environment that runs one application with its own dependencies.",
    "pgvector": "A PostgreSQL extension that stores vectors and finds the ones most similar to a given vector.",
    "llm": "Large language model: an AI system trained on lots of text that can understand and generate language.",
    "mcp": "Model Context Protocol: a standard way for AI applications to connect to external tools and data sources.",
    "database": "An organized system for storing data so it can be searched, updated, and managed reliably.",
}


@mcp.tool()
def get_word_definition(word: str) -> str:
    """Return a short definition of an English or technical word."""
    w = word.strip().lower()
    print(f"[MCP] get_word_definition called with: {w!r}", flush=True)
    if not w:
        return "No word was provided."
    if w in GLOSSARY:
        return f"{w}: {GLOSSARY[w]}"
    try:
        r = httpx.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(w)}", timeout=6)
        if r.status_code == 200:
            meaning = r.json()[0]["meanings"][0]
            definition = meaning["definitions"][0]["definition"]
            return f"{w} ({meaning.get('partOfSpeech', 'word')}): {definition}"
    except Exception as exc:
        print(f"[MCP] public dictionary lookup failed: {exc}", flush=True)
    return f"No definition was found for '{word}'."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")