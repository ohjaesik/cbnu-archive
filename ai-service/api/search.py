from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from services.metadata_analyzer import MetadataAnalyzer
from services.ranking import rank_projects

router = APIRouter(prefix="/search", tags=["search"])

analyzer = MetadataAnalyzer()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


# 실제로는 DB나 벡터DB에서 불러와야 함
DUMMY_PROJECTS = [
    {
        "project_id": 101,
        "title": "AI 인터렉션 기반 교내 프로젝트 지식 아카이브",
        "topic": "프로젝트 아카이브",
        "tech_stack": ["React", "Spring Boot", "PostgreSQL", "OpenSearch", "Python", "RAG", "LLM"],
        "keywords": ["검색", "추천", "자연어", "아카이브"],
        "difficulty": "고급",
        "project_type": "팀 프로젝트",
        "embedding": [0.0] * 384,  # 실제 임베딩으로 교체
    },
    {
        "project_id": 102,
        "title": "헬스케어 이미지 분류 시스템",
        "topic": "헬스케어",
        "tech_stack": ["PyTorch", "OpenCV", "Python"],
        "keywords": ["헬스케어", "이미지 분류", "딥러닝"],
        "difficulty": "중급",
        "project_type": "캡스톤",
        "embedding": [0.0] * 384,  # 실제 임베딩으로 교체
    },
]


@router.post("")
def search_projects(request: SearchRequest):
    query_vec = analyzer.embed_query(request.query)

    results = rank_projects(
        query=request.query,
        query_embedding=query_vec,
        project_items=DUMMY_PROJECTS,
        top_k=request.top_k,
    )
    return {
        "query": request.query,
        "count": len(results),
        "results": results,
    }