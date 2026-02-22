from typing import Literal
from unstructured_client import UnstructuredClient


async def get_chunks(
    client: UnstructuredClient,
    text: str,
    format: Literal["md", "html"],
    size: int,
    overlap: int = 100,
) -> list[str]:
    if not text:
        return []

    request = {
        "partition_parameters": {
            "files": {
                "content": text.encode("utf-8"),
                "file_name": f"source.{format}",
            },
            "strategy": "fast",
            "chunking_strategy": "by_title",
            "max_characters": size,
            "overlap": overlap,
            "combine_under_n_chars": size // 4,
            "multipage_sections": True,
        }
    }

    response = await client.general.partition_async(request=request)

    return [el["text"] for el in response.elements if "text" in el]
