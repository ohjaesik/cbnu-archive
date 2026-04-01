from __future__ import annotations

import re
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Tuple

from sentence_transformers import SentenceTransformer

from models.project import MetadataResult, ProjectInput

MODEL_NAME = "intfloat/multilingual-e5-small"

TECH_PATTERNS = {
    "React": [r"\breact\b", r"\bnext\.?js\b"],
    "Spring Boot": [r"\bspring\s*boot\b", r"\bspring\b"],
    "PostgreSQL": [r"\bpostgresql\b", r"\bpostgres\b"],
    "MySQL": [r"\bmysql\b"],
    "MongoDB": [r"\bmongodb\b", r"\bmongo\b"],
    "FastAPI": [r"\bfastapi\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "PyTorch": [r"\bpytorch\b", r"\btorch\b"],
    "TensorFlow": [r"\btensorflow\b", r"\btf\b"],
    "OpenCV": [r"\bopencv\b", r"\bcv2\b"],
    "OpenSearch": [r"\bopensearch\b", r"\belasticsearch\b"],
    "Qdrant": [r"\bqdrant\b"],
    "FAISS": [r"\bfaiss\b"],
    "MinIO": [r"\bminio\b"],
    "Docker": [r"\bdocker\b"],
    "Redis": [r"\bredis\b"],
    "Node.js": [r"\bnode\.?js\b", r"\bnode\b"],
    "Java": [r"\bjava\b"],
    "Python": [r"\bpython\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "Claude": [r"\bclaude\b"],
    "RAG": [r"\brag\b", r"retrieval[- ]augmented generation"],
    "LLM": [r"\bllm\b", r"large language model"],
}

TOPIC_PATTERNS = {
    "헬스케어": [r"헬스케어", r"의료", r"healthcare", r"medical"],
    "보안": [r"보안", r"security", r"attack", r"malware"],
    "추천 시스템": [r"추천", r"recommendation"],
    "프로젝트 아카이브": [r"아카이브", r"archive"],
    "컴퓨터 비전": [r"컴퓨터 비전", r"computer vision", r"image classification", r"object detection"],
    "자연어 처리": [r"자연어 처리", r"\bnlp\b", r"language model", r"텍스트 분류"],
    "웹 플랫폼": [r"웹", r"web platform", r"frontend", r"backend"],
    "챗봇": [r"챗봇", r"chatbot"],
    "교육": [r"교육", r"education", r"learning"],
}

PROJECT_TYPE_PATTERNS = {
    "캡스톤": [r"캡스톤", r"capstone"],
    "팀 프로젝트": [r"팀 프로젝트", r"team project"],
    "수업 과제": [r"과제", r"class project", r"assignment"],
    "해커톤": [r"해커톤", r"hackathon"],
}

KEYWORD_STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with",
    "is", "are", "this", "that", "we", "it", "be", "as", "by",
    "및", "그리고", "또한", "사용", "기반", "통해", "대한", "프로젝트", "시스템",
    "구현", "개발", "기능", "구조", "정리", "설계"
}

def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub("r\n{2,}", "\n", text)
    return text.strip()

def join_all_text(project: ProjectInput) -> str:
    parts = [
        project.short_summary,
        project.description,
        project.readme,
        project.report_text,
        " ".join(project.file_names),
        " ".join(project.folder_paths),
        " ".join(project.config_texts.values()),
        project.course_name,
        project.semester,
    ]
    return normalize_text("\n".join([p for p in parts if p]))
def find_matches(pattern_map: Dict[str, List[str]], text: str) -> List[str]:
    text_l = text.lower()
    found = []
    for label, patterns in pattern_map.items():
        for pat in patterns:
            if re.search(pat, text_l, re.IGNORECASE):
                found.append(label)
                break
    return sorted(set(found))


def infer_languages_from_files(file_names: List[str]) -> List[str]:
    ext_map = {
        ".py": "Python",
        ".java": "Java",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".jsx": "JavaScript",
        ".kt": "Kotlin",
        ".cpp": "C++",
        ".c": "C",
        ".cs": "C#",
        ".go": "Go",
        ".php": "PHP",
        ".rb": "Ruby",
        ".swift": "Swift",
        ".rs": "Rust",
    }
    langs = set()
    for name in file_names:
        suffix = Path(name).suffix.lower()
        if suffix in ext_map:
            langs.add(ext_map[suffix])
    return sorted(langs)


def infer_languages_from_config(config_texts: Dict[str, str]) -> List[str]:
    langs = set()
    for filename, _text in config_texts.items():
        fn = filename.lower()
        if "requirements.txt" in fn or "pyproject.toml" in fn:
            langs.add("Python")
        if "package.json" in fn:
            langs.update(["JavaScript", "TypeScript"])
        if "pom.xml" in fn or "build.gradle" in fn:
            langs.add("Java")
    return sorted(langs)


def extract_keywords(text: str, max_keywords: int = 12) -> List[str]:
    tokens = re.findall(r"[A-Za-z가-힣][A-Za-z0-9가-힣\-\+\.]{1,30}", text)
    counts: Dict[str, int] = {}

    for token in tokens:
        t = token.strip().lower()
        if len(t) < 2:
            continue
        if t in KEYWORD_STOPWORDS:
            continue
        if re.fullmatch(r"\d+", t):
            continue
        counts[t] = counts.get(t, 0) + 1

    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return [k for k, _ in ranked[:max_keywords]]


def infer_project_type(text: str) -> str | None:
    matches = find_matches(PROJECT_TYPE_PATTERNS, text)
    return matches[0] if matches else None


def infer_topic(text: str) -> Tuple[str | None, List[str]]:
    matches = find_matches(TOPIC_PATTERNS, text)
    if not matches:
        return None, []
    return matches[0], matches[1:]


def infer_input_output_type(text: str) -> List[str]:
    text_l = text.lower()
    types = []
    rules = [
        ("이미지 입력", [r"image", r"이미지", r"opencv", r"vision"]),
        ("텍스트 입력", [r"text", r"텍스트", r"nlp", r"query", r"질의"]),
        ("웹 서비스", [r"web", r"frontend", r"backend", r"react", r"spring"]),
        ("API 서비스", [r"api", r"fastapi", r"flask", r"spring boot"]),
        ("추천 응답", [r"recommend", r"추천"]),
        ("검색 응답", [r"search", r"검색"]),
    ]
    for label, patterns in rules:
        for pat in patterns:
            if re.search(pat, text_l, re.IGNORECASE):
                types.append(label)
                break
    return sorted(set(types))


def infer_difficulty(tech_stack: List[str], text: str) -> str:
    score = 0
    if len(tech_stack) >= 5:
        score += 1
    if any(x in tech_stack for x in ["PyTorch", "TensorFlow", "RAG", "LLM", "OpenSearch", "Qdrant", "FAISS"]):
        score += 2
    if any(x in tech_stack for x in ["Docker", "MinIO", "Redis", "PostgreSQL"]):
        score += 1

    text_l = text.lower()
    if re.search(r"rag|vector|embedding|semantic search|시맨틱 검색|권한 관리|분산", text_l):
        score += 1

    if score <= 1:
        return "초급"
    if score <= 3:
        return "중급"
    return "고급"


def build_searchable_text(project: ProjectInput, topic: str | None, tech_stack: List[str], keywords: List[str]) -> str:
    parts = [
        project.title,
        project.short_summary,
        project.description,
        f"과목명: {project.course_name}",
        f"학기: {project.semester}",
        f"주제: {topic or ''}",
        f"기술 스택: {', '.join(tech_stack)}",
        f"핵심 키워드: {', '.join(keywords)}",
        project.readme[:2000],
    ]
    return normalize_text("\n".join([p for p in parts if p]))


class MetadataAnalyzer:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = SentenceTransformer(model_name)

    def analyze(self, project: ProjectInput) -> MetadataResult:
        merged_text = join_all_text(project)

        tech_stack = find_matches(TECH_PATTERNS, merged_text)

        languages = sorted(set(
            infer_languages_from_files(project.file_names)
            + infer_languages_from_config(project.config_texts)
            + [x for x in tech_stack if x in {"Python", "Java", "JavaScript", "TypeScript"}]
        ))

        topic, sub_topics = infer_topic(merged_text)
        keywords = extract_keywords(merged_text)
        project_type = infer_project_type(merged_text)
        difficulty = infer_difficulty(tech_stack, merged_text)
        io_types = infer_input_output_type(merged_text)

        searchable_text = build_searchable_text(project, topic, tech_stack, keywords)
        passage_text = f"passage: {searchable_text}"

        embedding = self.model.encode(
            passage_text,
            normalize_embeddings=True,
        )

        return MetadataResult(
            project_id=project.project_id,
            topic=topic,
            sub_topics=sub_topics,
            tech_stack=tech_stack,
            languages=languages,
            keywords=keywords,
            project_type=project_type,
            difficulty=difficulty,
            input_output_type=io_types,
            searchable_text=searchable_text,
            passage_text=passage_text,
            embedding_dim=len(embedding),
            embedding=embedding.tolist(),
        )

    def embed_query(self, query: str) -> List[float]:
        query_text = f"query: {query.strip()}"
        emb = self.model.encode(query_text, normalize_embeddings=True)
        return emb.tolist()
    