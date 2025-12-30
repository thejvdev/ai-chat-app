from typing import AsyncIterator
import json
from langchain_ollama import ChatOllama

title_llm = ChatOllama(model="llama3", temperature=0, format="json")
chat_llm = ChatOllama(model="llama3", temperature=0.2)


async def create_title(query: str) -> str:
    prompt = (
        'Return ONLY valid JSON like {"title":"..."}.\n'
        "Rules: short title, max 3 words.\n"
        f"Query:\n{query}\n"
    )

    result = await title_llm.ainvoke(prompt)

    try:
        data = json.loads(result.content)
        title = str(data.get("title", "")).strip()
        return title or "New chat"
    except Exception:
        return "New chat"


async def ask(history: list) -> AsyncIterator[str]:
    async for chunk in chat_llm.astream(history):
        if chunk.content:
            yield chunk.content
