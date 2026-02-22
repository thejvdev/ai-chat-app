import asyncio
from typing import Literal
from datetime import datetime, timezone
from loguru import logger

import trafilatura
from httpx import AsyncClient
from app.core.config import SEARXNG_API_URL


async def search(client: AsyncClient, query: str, categories: str) -> dict:
    response = await client.get(
        f"{SEARXNG_API_URL}/search",
        params={
            "q": query,
            "format": "json",
            "categories": categories,
        },
    )
    response.raise_for_status()
    return response.json()


async def multi_search(
    client: AsyncClient, queries: list[str], categories: str
) -> list[dict]:
    if not queries:
        return []

    async def safe_search(query: str):
        try:
            return await search(client=client, query=query, categories=categories)
        except Exception as e:
            logger.error(f"Unexpected error in multi_search for query '{query}': {e}")
            return {"results": []}

    tasks = [safe_search(query) for query in queries]
    return await asyncio.gather(*tasks)


async def fetch_html(client: AsyncClient, url: str) -> str:
    response = await client.get(url, timeout=20)
    response.raise_for_status()
    return response.text


def parse_html(html: str, format: Literal["markdown", "html"]) -> str | None:
    text = trafilatura.extract(html, output_format=format, include_tables=True)
    if text and len(text) > 200:
        return text
    return None


async def extract_text_async(
    client: AsyncClient, url: str, format: Literal["markdown", "html"]
) -> str | None:
    html = await fetch_html(client, url)
    return await asyncio.to_thread(parse_html, html, format)


async def multi_extract(
    client: AsyncClient,
    urls: list[str],
    format: Literal["markdown", "html"],
    limit: int = 10,
) -> list[str | None]:
    if not urls:
        return []

    sem = asyncio.Semaphore(limit)

    async def worker(url: str) -> str | None:
        async with sem:
            try:
                return await extract_text_async(client, url, format)
            except Exception as e:
                logger.error(f"Unexpected error in multi_extract for url '{url}': {e}")
                return None

    tasks = [worker(url) for url in urls]
    return await asyncio.gather(*tasks)


async def web_parse(
    client: AsyncClient,
    queries: list[str],
    categories: list[str],
    limit_per_query: int = 5,
    format: Literal["markdown", "html"] = "html",
) -> list[dict]:
    cats_str = ",".join(cat.strip() for cat in categories)

    responses = await multi_search(
        client=client,
        queries=queries,
        categories=cats_str,
    )
    if not responses:
        return []

    seen = set()
    pages = []
    urls = []
    for response in responses:
        added = 0
        for page in response.get("results", []):
            if added >= limit_per_query:
                break

            url = page.get("url")
            if url and url not in seen:
                seen.add(url)
                pages.append(page)
                urls.append(url)
                added += 1

    texts = await multi_extract(client, urls, format)
    if not texts:
        return []

    records = []
    for page, text in zip(pages, texts):
        if text is None:
            continue

        records.append(
            {
                "content": text,
                "metadata": {
                    "title": page.get("title", ""),
                    "url": page.get("url", ""),
                    "created_at": datetime.now(timezone.utc),
                },
            }
        )

    return records
