from __future__ import annotations

from typing import Any, Dict, List

from services.metadata_analyzer import MetadataAnalyzer
from services.ranking import rank_projects
from services.llm_service import LocalLLMService


class RAGService:
    def __init__(self):
        self.analyzer = MetadataAnalyzer()
        self.llm_service = LocalLLMService()

    def run_rag(
        self,
        query: str,
        project_items: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        query_embedding = self.analyzer.embed_query(query)

        ranked_projects = rank_projects(
            query=query,
            query_embedding=query_embedding,
            project_items=project_items,
            top_k=top_k,
        )

        answer = self.llm_service.generate_answer(
            query=query,
            ranked_projects=ranked_projects,
        )

        return {
            "query": query,
            "count": len(ranked_projects),
            "results": ranked_projects,
            "answer": answer,
        }