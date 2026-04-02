from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from services.rag_service import RAGService

router = APIRouter(prefix="/search", tags=["search"])

rag_service = RAGService()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


# 실제론 DB/벡터DB에서 가져와야 함
DUMMY_PROJECTS = [
    {
        "project_id": 101,
        "title": "AI 인터렉션 기반 교내 프로젝트 지식 아카이브",
        "topic": "프로젝트 아카이브",
        "tech_stack": ["React", "Spring Boot", "PostgreSQL", "OpenSearch", "Python", "RAG", "LLM"],
        "keywords": ["검색", "추천", "자연어", "아카이브"],
        "difficulty": "고급",
        "project_type": "팀 프로젝트",
        "embedding": [0.01] * 384,
    },
    {
        "project_id": 102,
        "title": "헬스케어 이미지 분류 시스템",
        "topic": "헬스케어",
        "tech_stack": ["PyTorch", "OpenCV", "Python"],
        "keywords": ["헬스케어", "이미지 분류", "딥러닝"],
        "difficulty": "중급",
        "project_type": "캡스톤",
        "embedding": [0.02] * 384,
    },
    {
        "project_id": 103,
        "title": "추천 시스템 기반 도서 추천 플랫폼",
        "topic": "추천 시스템",
        "tech_stack": ["FastAPI", "PostgreSQL", "Python"],
        "keywords": ["추천", "도서", "검색"],
        "difficulty": "중급",
        "project_type": "수업 과제",
        "embedding": [0.03] * 384,
    },
]


@router.post("")
def search_projects(request: SearchRequest):
    result = rag_service.run_rag(
        query=request.query,
        project_items=DUMMY_PROJECTS,
        top_k=request.top_k,
    )
    return result