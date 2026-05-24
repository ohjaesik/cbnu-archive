from __future__ import annotations

from typing import Any


def build_rag_context(
    search_results: list[dict[str, Any]],
    max_items: int = 5,
    max_chars_per_item: int = 1200,
) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []

    for idx, item in enumerate(search_results[:max_items], start=1):
        metadata = item.get("metadata", {}) or {}

        title = item.get("title") or metadata.get("title") or ""
        summary = metadata.get("summary") or ""
        description = metadata.get("description") or ""
        language = metadata.get("language") or ""
        keywords = metadata.get("keywords") or []
        tech_stack = metadata.get("tech_stack") or []

        if not isinstance(keywords, list):
            keywords = [str(keywords)]
        if not isinstance(tech_stack, list):
            tech_stack = [str(tech_stack)]

        project_id = item.get("project_id") or item.get("_id")
        score = item.get("score", 0.0)
        embedding_score = item.get("embedding_score", 0.0)
        metadata_score = item.get("metadata_score", 0.0)
        explanation = item.get("explanation", "")

        context_text = "\n".join(
            [
                f"[검색순위 {idx}]",
                f"project_id: {project_id}",
                f"title: {title}",
                f"score: {score}",
                f"embedding_score: {embedding_score}",
                f"metadata_score: {metadata_score}",
                f"match_reason: {explanation}",
                f"summary: {summary}",
                f"description: {description}",
                f"language: {language}",
                f"keywords: {', '.join(map(str, keywords))}",
                f"tech_stack: {', '.join(map(str, tech_stack))}",
            ]
        )

        contexts.append(
            {
                "rank": idx,
                "project_id": project_id,
                "title": title,
                "context_text": context_text[:max_chars_per_item],
                "score": score,
                "embedding_score": embedding_score,
                "metadata_score": metadata_score,
                "explanation": explanation,
                "metadata": metadata,
            }
        )

    return contexts