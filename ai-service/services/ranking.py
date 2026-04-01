from __future__ import annotations

from typing import Any, Dict, List

import numpy as np


def cosine_similarity(a: List[float], b: List[float]) -> float:
    a_np = np.array(a, dtype=np.float32)
    b_np = np.array(b, dtype=np.float32)

    a_norm = np.linalg.norm(a_np)
    b_norm = np.linalg.norm(b_np)

    if a_norm == 0 or b_norm == 0:
        return 0.0

    return float(np.dot(a_np, b_np) / (a_norm * b_norm))


def normalize_text_for_match(text: str) -> str:
    return text.strip().lower()


def metadata_match_score(query: str, item: Dict[str, Any]) -> float:
    score = 0.0
    q = normalize_text_for_match(query)

    tech_stack = [normalize_text_for_match(x) for x in item.get("tech_stack", [])]
    topic = normalize_text_for_match(item.get("topic", "") or "")
    keywords = [normalize_text_for_match(x) for x in item.get("keywords", [])]
    difficulty = normalize_text_for_match(item.get("difficulty", "") or "")
    project_type = normalize_text_for_match(item.get("project_type", "") or "")

    known_stack_terms = [
        "react", "spring", "spring boot", "python", "java", "javascript",
        "typescript", "pytorch", "tensorflow", "opencv", "postgresql",
        "mysql", "mongodb", "fastapi", "flask", "django", "opensearch",
        "qdrant", "faiss", "docker", "redis"
    ]
    for term in known_stack_terms:
        if term in q and any(term in s for s in tech_stack):
            score += 0.25

    known_topics = [
        "헬스케어", "보안", "추천", "추천 시스템", "아카이브",
        "컴퓨터 비전", "자연어 처리", "챗봇", "교육", "웹"
    ]
    for term in known_topics:
        term_l = term.lower()
        if term_l in q:
            if term_l in topic:
                score += 0.3
            if any(term_l in k for k in keywords):
                score += 0.15

    if ("초급" in q or "입문" in q or "beginner" in q) and difficulty == "초급":
        score += 0.2
    if ("중급" in q or "intermediate" in q) and difficulty == "중급":
        score += 0.2
    if ("고급" in q or "advanced" in q) and difficulty == "고급":
        score += 0.2

    if ("캡스톤" in q and "캡스톤" in project_type):
        score += 0.2
    if ("팀 프로젝트" in q and "팀 프로젝트" in project_type):
        score += 0.2
    if ("과제" in q and "수업 과제" in project_type):
        score += 0.2

    return score


def build_reason(query: str, item: Dict[str, Any]) -> List[str]:
    reasons = []
    q = normalize_text_for_match(query)

    tech_stack = item.get("tech_stack", [])
    topic = item.get("topic")
    difficulty = item.get("difficulty")
    project_type = item.get("project_type")

    stack_terms = [
        "React", "Spring Boot", "Python", "Java", "JavaScript", "TypeScript",
        "PyTorch", "TensorFlow", "OpenCV", "PostgreSQL", "FastAPI", "Docker",
        "OpenSearch", "Qdrant", "FAISS"
    ]

    for term in stack_terms:
        if term.lower() in q and term in tech_stack:
            reasons.append(f"{term} 기술 스택이 일치함")

    if topic and normalize_text_for_match(topic) in q:
        reasons.append(f"'{topic}' 주제가 질의와 유사함")

    if difficulty and difficulty in query:
        reasons.append(f"요청한 난이도({difficulty})와 일치함")

    if project_type and project_type in query:
        reasons.append(f"프로젝트 유형({project_type})이 일치함")

    if not reasons:
        reasons.append("문서 의미 유사도가 높음")

    return reasons[:3]


def rank_projects(
    query: str,
    query_embedding: List[float],
    project_items: List[Dict[str, Any]],
    top_k: int = 5,
    embedding_weight: float = 0.8,
    metadata_weight: float = 0.2,
) -> List[Dict[str, Any]]:
    ranked = []

    for item in project_items:
        emb = item.get("embedding")
        if not emb:
            continue

        semantic_score = cosine_similarity(query_embedding, emb)
        meta_score = metadata_match_score(query, item)
        final_score = (semantic_score * embedding_weight) + (meta_score * metadata_weight)

        ranked.append({
            "project_id": item.get("project_id"),
            "title": item.get("title"),
            "topic": item.get("topic"),
            "tech_stack": item.get("tech_stack", []),
            "difficulty": item.get("difficulty"),
            "project_type": item.get("project_type"),
            "semantic_score": round(semantic_score, 4),
            "metadata_score": round(meta_score, 4),
            "final_score": round(final_score, 4),
            "reasons": build_reason(query, item),
        })

    ranked.sort(key=lambda x: x["final_score"], reverse=True)

    for idx, item in enumerate(ranked[:top_k], start=1):
        item["rank"] = idx

    return ranked[:top_k]


def aggregate_chunk_results(chunk_results: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    grouped: Dict[int, Dict[str, Any]] = {}

    for item in chunk_results:
        pid = item["project_id"]
        if pid not in grouped:
            grouped[pid] = {
                "project_id": pid,
                "title": item["title"],
                "topic": item.get("topic"),
                "tech_stack": item.get("tech_stack", []),
                "difficulty": item.get("difficulty"),
                "project_type": item.get("project_type"),
                "best_score": item["final_score"],
                "reasons": set(item.get("reasons", [])),
            }
        else:
            grouped[pid]["best_score"] = max(grouped[pid]["best_score"], item["final_score"])
            grouped[pid]["reasons"].update(item.get("reasons", []))

    merged = []
    for idx, value in enumerate(
        sorted(grouped.values(), key=lambda x: x["best_score"], reverse=True)[:top_k],
        start=1
    ):
        merged.append({
            "rank": idx,
            "project_id": value["project_id"],
            "title": value["title"],
            "topic": value["topic"],
            "tech_stack": value["tech_stack"],
            "difficulty": value["difficulty"],
            "project_type": value["project_type"],
            "final_score": round(value["best_score"], 4),
            "reasons": list(value["reasons"])[:3],
        })

    return merged