import asyncio

from mcp import ClientSession

try:
    from mcp.client.streamable_http import streamablehttp_client as _http_client
except ImportError:
    from mcp.client.streamable_http import streamable_http_client as _http_client

from .config import settings


async def _call(word: str) -> str:
    url = settings.MCP_SERVER_URL.rstrip("/") + "/mcp"
    async with _http_client(url) as streams:
        read, write = streams[0], streams[1]
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_word_definition", {"word": word})
            return "\n".join(c.text for c in result.content if getattr(c, "text", None))


def get_word_definition(word: str) -> str:
    return asyncio.run(_call(word))