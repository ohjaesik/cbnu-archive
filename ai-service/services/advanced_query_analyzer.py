
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class QueryAnalysisResult:
    raw_query: str
    normalized_query: str
    topic_terms: list[str] = field(default_factory=list)
    tech_stack_terms: list[str] = field(default_factory=list)
    keyword_terms: list[str] = field(default_factory=list)
    difficulty_terms: list[str] = field(default_factory=list)
    intent_type: str = "general"


TECH_ALIASES = {
    "react": "React",
    "리액트": "React",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "java": "Java",
    "python": "Python",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "opencv": "OpenCV",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "docker": "Docker",
    "yolo": "YOLO",
    "unity": "Unity",
    "mediapipe": "MediaPipe",
}

TOPIC_ALIASES = {
    # recommendation / ranking 계열
    "추천 시스템": "recommendation",
    "추천시스템": "recommendation",
    "추천 알고리즘": "recommendation",
    "추천알고리즘": "recommendation",
    "피드 랭킹": "recommendation",
    "피드랭킹": "recommendation",
    "랭킹 알고리즘": "recommendation",
    "ranking algorithm": "recommendation",
    "recommendation system": "recommendation",
    "recommendation algorithm": "recommendation",

    # RAG / search 계열
    "rag": "rag",
    "문서 검색": "document search",
    "문서검색": "document search",
    "코드 검색": "code search",
    "코드검색": "code search",
    "검색 시스템": "search system",

    # image generation 계열
    "이미지 생성 ai": "image generation",
    "이미지 생성": "image generation",
    "생성 ai": "generative ai",
    "stable diffusion": "stable diffusion",
    "스테이블 디퓨전": "stable diffusion",

    # android / mirroring 계열
    "안드로이드": "android",
    "android": "android",
    "화면 미러링": "screen mirroring",
    "미러링": "screen mirroring",
    "스크린 미러링": "screen mirroring",

    # general topics
    "챗봇": "chatbot",
    "교육": "education",
    "학습": "education",
    "컴퓨터 비전": "computer vision",
    "비전": "computer vision",
    "객체 탐지": "object detection",
    "자연어 처리": "natural language processing",
    "자연어": "natural language processing",
    "nlp": "natural language processing",
    "시스템 디자인": "system design",
    "시스템 설계": "system design",
    "상권 분석": "business district analysis",
    "안전장비": "ppe detection",
    "안전": "safety",
    "헬멧": "helmet",
    "감정": "emotion",
    "게임": "game",
}

DIFFICULTY_ALIASES = {
    "쉬운": "beginner",
    "초급": "beginner",
    "간단한": "beginner",
    "중급": "intermediate",
    "고급": "advanced",
    "어려운": "advanced",
    "복잡한": "advanced",
}


def normalize_query(query: str) -> str:
    return " ".join((query or "").strip().lower().split())


def _append_unique(target: list[str], value: str) -> None:
    if value and value not in target:
        target.append(value)


def infer_intent_type(
    topic_terms: list[str],
    tech_stack_terms: list[str],
    keyword_terms: list[str],
) -> str:
    if tech_stack_terms and topic_terms:
        return "compound"
    if tech_stack_terms:
        return "tech_stack"
    if topic_terms:
        return "topic"
    if keyword_terms:
        return "keyword"
    return "general"


def analyze_query(query: str) -> QueryAnalysisResult:
    normalized = normalize_query(query)

    tech_stack_terms: list[str] = []
    topic_terms: list[str] = []
    keyword_terms: list[str] = []
    difficulty_terms: list[str] = []

    for key, value in sorted(TECH_ALIASES.items(), key=lambda x: -len(x[0])):
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(key.lower()) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, normalized):
            _append_unique(tech_stack_terms, value)

    for key, value in sorted(TOPIC_ALIASES.items(), key=lambda x: -len(x[0])):
        if key.lower() in normalized:
            _append_unique(topic_terms, value)

    for key, value in sorted(DIFFICULTY_ALIASES.items(), key=lambda x: -len(x[0])):
        if key.lower() in normalized:
            _append_unique(difficulty_terms, value)

    tokens = re.findall(r"[A-Za-z가-힣][A-Za-z0-9가-힣\-\+]{1,30}", normalized)
    stopwords = {
        "프로젝트", "찾아줘", "찾아", "만든", "사용한", "기반", "관련", "있는",
        "으로", "로", "중", "것", "거", "추천해줘", "보여줘", "알려줘",
        "비슷한", "활용한", "사용해서", "개발한", "정리해줘",
        "project", "using", "with", "based", "show", "find", "recommend",
    }
    alias_keys = set(TECH_ALIASES.keys()) | set(TOPIC_ALIASES.keys()) | set(DIFFICULTY_ALIASES.keys())

    for token in tokens:
        if token in stopwords:
            continue
        if token in alias_keys:
            continue
        _append_unique(keyword_terms, token)

    intent_type = infer_intent_type(topic_terms, tech_stack_terms, keyword_terms)

    return QueryAnalysisResult(
        raw_query=query,
        normalized_query=normalized,
        topic_terms=topic_terms,
        tech_stack_terms=tech_stack_terms,
        keyword_terms=keyword_terms,
        difficulty_terms=difficulty_terms,
        intent_type=intent_type,
    )
