from __future__ import annotations

import math
import re
from typing import Any

from services.advanced_query_analyzer import analyze_query


BROAD_TERMS = {
    "ai",
    "rag",
    "search",
    "education",
    "project",
    "backend",
    "web",
    "tool",
    "system",
    "learning",
}


HIGH_VALUE_TERMS = {
    "spring boot",
    "stable diffusion",
    "screen mirroring",
    "android",
    "feed ranking",
    "recommendation",
    "recommendation system",
    "recommendation algorithm",
    "document search",
    "code search",
    "rag",
    "retrieval augmented generation",
    "ppe detection",
    "object detection",
    "computer vision",
    "natural language processing",
}

def _norm(value: str) -> str:
    return " ".join((value or "").lower().split())


def _lower_list(values: list[str] | None) -> list[str]:
    return [_norm(v) for v in (values or []) if _norm(v)]


def _contains(text: str, term: str) -> bool:
    text_norm = _norm(text)
    term_norm = _norm(term)

    if not text_norm or not term_norm:
        return False

    # 짧은 단어는 부분 문자열 매칭 금지
    # 예: anuraghazra 안의 rag, deepseek-ai 안의 ai 과대매칭 방지
    if len(term_norm) <= 3:
        pattern = r"(?<![a-z0-9])" + re.escape(term_norm) + r"(?![a-z0-9])"
        return re.search(pattern, text_norm) is not None

    # 공백이 있는 phrase는 그대로 포함 여부 확인
    if " " in term_norm:
        return term_norm in text_norm

    # 일반 단어도 token boundary 기준으로 확인
    pattern = r"(?<![a-z0-9])" + re.escape(term_norm) + r"(?![a-z0-9])"
    return re.search(pattern, text_norm) is not None


def _term_weight(term: str) -> float:
    term_norm = _norm(term)

    if term_norm in HIGH_VALUE_TERMS:
        return 1.8

    if term_norm in BROAD_TERMS:
        return 0.35

    if len(term_norm) <= 3:
        return 0.25

    if " " in term_norm:
        return 1.4

    return 1.0


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0

    numerator = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return numerator / (norm_a * norm_b)


def calculate_metadata_score(query: str, project: dict[str, Any]) -> tuple[float, list[str]]:
    intent = analyze_query(query)
    metadata = project.get("metadata", project) or {}

    title = _norm(project.get("title", ""))
    project_id = _norm(project.get("project_id") or project.get("_id") or "")
    summary = _norm(metadata.get("summary", ""))
    description = _norm(metadata.get("description", ""))
    language = _norm(metadata.get("language", ""))

    text_blob = " ".join(
        [
            title,
            project_id,
            summary,
            description,
            language,
        ]
    )

    keywords = _lower_list(metadata.get("keywords", []))
    tech_stack = _lower_list(metadata.get("tech_stack", []))

    score = 0.0
    reasons: list[str] = []

    def add_score(base: float, term: str, reason: str) -> None:
        nonlocal score

        weight = _term_weight(term)
        value = base * weight

        if value <= 0:
            return

        score += value
        reasons.append(reason)

    for tech in intent.tech_stack_terms:
        tech_norm = _norm(tech)

        if tech_norm in tech_stack:
            add_score(4.0, tech, f"기술 스택 일치: {tech}")

        elif _contains(title, tech_norm) or _contains(project_id, tech_norm):
            add_score(3.2, tech, f"제목/저장소명 내 기술 일치: {tech}")

        elif _contains(text_blob, tech_norm):
            add_score(1.5, tech, f"본문 내 기술 언급: {tech}")

    for topic in intent.topic_terms:
        topic_norm = _norm(topic)
        is_broad = topic_norm in BROAD_TERMS or len(topic_norm) <= 3

        if topic_norm in keywords:
            add_score(3.2, topic, f"키워드 일치: {topic}")

        elif not is_broad and (
            _contains(title, topic_norm) or _contains(project_id, topic_norm)
        ):
            add_score(2.8, topic, f"제목/저장소명 내 주제 일치: {topic}")

        elif _contains(summary, topic_norm):
            base = 0.8 if is_broad else 1.8
            add_score(base, topic, f"요약 내 주제 언급: {topic}")

        elif not is_broad and _contains(description, topic_norm):
            add_score(1.0, topic, f"설명 내 주제 언급: {topic}")

    for keyword in intent.keyword_terms:
        keyword_norm = _norm(keyword)
        is_broad = keyword_norm in BROAD_TERMS or len(keyword_norm) <= 3

        if is_broad:
            base_keyword_score = 0.15
        else:
            base_keyword_score = 1.0

        if keyword_norm in keywords:
            add_score(
                base_keyword_score * 1.5,
                keyword,
                f"질의어와 키워드 일치: {keyword}",
            )

        elif not is_broad and (
            _contains(title, keyword_norm) or _contains(project_id, keyword_norm)
        ):
            add_score(
                base_keyword_score * 1.4,
                keyword,
                f"질의어와 제목/저장소명 일치: {keyword}",
            )

        elif _contains(summary, keyword_norm):
            add_score(
                base_keyword_score * 0.8,
                keyword,
                f"질의어가 요약에 포함: {keyword}",
            )

        elif not is_broad and _contains(description, keyword_norm):
            add_score(
                base_keyword_score * 0.45,
                keyword,
                f"질의어가 설명에 포함: {keyword}",
            )

    for difficulty in intent.difficulty_terms:
        diff_norm = _norm(difficulty)

        if _contains(text_blob, diff_norm):
            add_score(0.8, difficulty, f"난이도 조건 언급: {difficulty}")

    return score, reasons


def _has_strong_match(reasons: list[str]) -> bool:
    strong_markers = [
        "기술 스택 일치",
        "키워드 일치",
        "제목/저장소명 내 기술 일치",
        "제목/저장소명 내 주제 일치",
        "질의어와 제목/저장소명 일치",
    ]

    return any(any(marker in reason for marker in strong_markers) for reason in reasons)


def rerank_projects(
    query: str,
    query_embedding: list[float] | None,
    candidates: list[dict[str, Any]],
    top_k: int = 10,
    embedding_weight: float = 0.55,
    metadata_weight: float = 0.45,
) -> list[dict[str, Any]]:
    raw_rows: list[dict[str, Any]] = []
    max_metadata_score = 0.0

    for item in candidates:
        embedding_score = 0.0

        if query_embedding is not None and item.get("embedding") is not None:
            embedding_score = cosine_similarity(query_embedding, item["embedding"])

        raw_metadata_score, reasons = calculate_metadata_score(query, item)
        max_metadata_score = max(max_metadata_score, raw_metadata_score)

        raw_rows.append(
            {
                "item": item,
                "embedding_score": embedding_score,
                "raw_metadata_score": raw_metadata_score,
                "match_reasons": reasons,
                "has_strong_match": _has_strong_match(reasons),
            }
        )

    reranked: list[dict[str, Any]] = []

    for row in raw_rows:
        normalized_metadata_score = (
            row["raw_metadata_score"] / max_metadata_score
            if max_metadata_score > 0
            else 0.0
        )

        final_score = (
            embedding_weight * row["embedding_score"]
            + metadata_weight * normalized_metadata_score
        )

        # metadata 매칭이 전혀 없으면 embedding만으로 상위에 과도하게 올라오지 않도록 감점
        if row["raw_metadata_score"] == 0:
            final_score *= 0.72

        # 약한 broad match만 있는 경우 추가 감점
        elif not row["has_strong_match"]:
            final_score *= 0.88

        item = dict(row["item"])
        item["embedding_score"] = round(row["embedding_score"], 6)
        item["metadata_score"] = round(normalized_metadata_score, 6)
        item["raw_metadata_score"] = round(row["raw_metadata_score"], 6)
        item["score"] = round(final_score, 6)
        item["match_reasons"] = row["match_reasons"][:3]
        item["explanation"] = build_result_explanation(item)

        reranked.append(item)

    reranked.sort(key=lambda x: x["score"], reverse=True)
    return reranked[:top_k]


def build_result_explanation(item: dict[str, Any]) -> str:
    reasons = item.get("match_reasons", [])

    if not reasons:
        return "임베딩 유사도가 높아 검색 결과에 포함되었습니다."

    return " / ".join(reasons)