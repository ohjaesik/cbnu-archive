from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from services.embedding_service import EmbeddingService
from services.search_service import search_projects
from services.rag_context_builder import build_rag_context
from services.rag_prompt_builder import build_rag_prompt
from services.local_llm_answer_service import LocalLLMAnswerService


class RAGPipeline:
    def __init__(
        self,
        corpus_path: str | Path,
        top_k: int = 5,
        model_name: str | None = None,
        build_corpus_embeddings: bool = True,
        use_llm: bool = False,
    ):
        self.corpus_path = Path(corpus_path)
        self.top_k = top_k
        self.use_llm = use_llm

        self.embedding_service = EmbeddingService()
        self.answer_service = (
            LocalLLMAnswerService(model_name=model_name)
            if use_llm
            else None
        )

        self.corpus = self._load_corpus()

        if build_corpus_embeddings:
            self._attach_corpus_embeddings()

    def _load_corpus(self) -> list[dict[str, Any]]:
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"corpus not found: {self.corpus_path}")

        rows: list[dict[str, Any]] = []

        with self.corpus_path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                row = json.loads(line)
                metadata = row.get("metadata", {}) or {}

                rows.append(
                    {
                        "project_id": row.get("_id"),
                        "_id": row.get("_id"),
                        "title": row.get("title", ""),
                        "text": row.get("text", ""),
                        "metadata": metadata,
                    }
                )

        return rows

    def _attach_corpus_embeddings(self) -> None:
        for idx, item in enumerate(self.corpus, start=1):
            text = item.get("text", "")
            if not text:
                item["embedding"] = []
                continue

            item["embedding"] = self.embedding_service.embed_passage(text)

            if idx % 20 == 0:
                print(f"[RAGPipeline] embedded corpus: {idx}/{len(self.corpus)}")

    def retrieve(self, query: str) -> dict[str, Any]:
        query_embedding = self.embedding_service.embed_query(query)

        return search_projects(
            query=query,
            query_embedding=query_embedding,
            candidates=self.corpus,
            top_k=self.top_k,
        )

    def run(self, query: str) -> dict[str, Any]:
        search_result = self.retrieve(query)

        search_results = search_result.get("results", [])
        contexts = build_rag_context(search_results, max_items=self.top_k)
        prompt = build_rag_prompt(query, contexts)

        raw_llm_answer = None

        if self.use_llm and self.answer_service is not None:
            raw_llm_answer = self.answer_service.generate(
                query=query,
                prompt=prompt,
                contexts=contexts,
            )

        answer = self._build_grounded_answer(
            query=query,
            contexts=contexts,
            llm_answer=raw_llm_answer,
        )

        return {
            "query": query,
            "answer": answer,
            "contexts": contexts,
            "search_results": search_results,
            "prompt": prompt,
        }
    
    def _build_grounded_answer(
        self,
        query: str,
        contexts: list[dict[str, Any]],
        llm_answer: str | None = None,
    ) -> str:
        if not contexts:
            return (
                "검색 결과를 찾지 못했습니다.\n"
                "질의를 더 구체적으로 입력하거나 기술 스택, 주제, 키워드를 포함해 다시 검색해보세요."
            )

        top = contexts[0]
        top_score = float(top.get("score", 0.0) or 0.0)
        top_metadata_score = float(top.get("metadata_score", 0.0) or 0.0)

        if top_metadata_score == 0.0 and top_score < 0.45:
            return (
                "질의와 직접적으로 관련된 프로젝트를 찾지 못했습니다.\n"
                f"- 입력 질의: {query}\n"
                "- 현재 상위 후보들은 임베딩 유사도만으로 검색되었고, 메타데이터 기준의 명확한 주제/기술 매칭은 없습니다.\n"
                "- 관련 프로젝트를 찾으려면 corpus에 RAG, 문서 검색, 추천 시스템, 피드 랭킹 관련 metadata가 포함되어야 합니다."
            )

        others = [
            item for item in contexts[1:]
            if float(item.get("metadata_score", 0.0) or 0.0) > 0.0
            or float(item.get("score", 0.0) or 0.0) >= 0.5
        ][:2]

        lines = [
            "1. 가장 적합한 프로젝트",
            f"- 프로젝트명: {top.get('title')} ({top.get('project_id')})",
            f"- 추천 이유: {top.get('explanation') or '검색 점수와 문서 유사도가 가장 높습니다.'}",
            f"- 검색 점수: {top.get('score')}",
            "",
            "2. 추가로 볼 만한 프로젝트",
        ]

        if others:
            for item in others:
                related_note = "추가 후보이지만 직접 관련성은 낮을 수 있습니다."
                if float(item.get("metadata_score", 0.0) or 0.0) > 0:
                    related_note = "질의 조건과 일부 메타데이터가 일치합니다."

                lines.extend(
                    [
                        f"- 프로젝트명: {item.get('title')} ({item.get('project_id')})",
                        f"  - 추천 이유: {item.get('explanation')}",
                        f"  - 관련성 판단: {related_note}",
                    ]
                )
        else:
            lines.append("- 추가 후보가 없습니다.")

        lines.extend(
            [
                "",
                "3. 추천 순위 요약",
            ]
        )
        reliable_contexts = [
            item for item in contexts
            if float(item.get("metadata_score", 0.0) or 0.0) > 0.0
            or float(item.get("score", 0.0) or 0.0) >= 0.65
        ]

        if not reliable_contexts:
            reliable_contexts = contexts[:1]

        for idx, item in enumerate(reliable_contexts[:3], start=1):
            lines.append(
                f"- {idx}순위: {item.get('title')} "
                f"({item.get('project_id')}) / score={item.get('score')}"
            )
            
        if llm_answer:
            lines.extend(
                [
                    "",
                    "4. LLM 보조 설명",
                    llm_answer.strip(),
                ]
            )

        return "\n".join(lines)