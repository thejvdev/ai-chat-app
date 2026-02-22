def format_rag_context(documents: list[dict]) -> str:
    if not documents:
        return "No relevant information found in the knowledge base."

    context_parts = []
    for i, doc in enumerate(documents, 1):
        content = doc.get("content", "Empty content")
        metadata = doc.get("metadata", {})
        source = metadata.get("url", "Unknown Source")

        part = f"--- SOURCE {i} ({source}) ---\n{content.strip()}"
        context_parts.append(part)

    return "\n\n".join(context_parts)
