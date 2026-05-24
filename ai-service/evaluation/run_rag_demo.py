from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from services.rag_pipeline import RAGPipeline


def main():
    corpus_path = ROOT / "dataset" / "retrieval" / "corpus_resolved.jsonl"
    output_path = ROOT / "dataset" / "retrieval" / "rag_demo_results.json"

    demo_queries = [
        "Spring Boot로 만든 백엔드 프로젝트 찾아줘",
        "RAG나 문서 검색과 관련된 프로젝트 추천해줘",
        "이미지 생성 AI 관련 프로젝트 있어?",
        "안드로이드 화면 미러링 도구 찾아줘",
        "추천 시스템이나 피드 랭킹 관련 프로젝트 알려줘",
    ]

    pipeline = RAGPipeline(
        corpus_path=corpus_path,
        top_k=5,
    )

    results = []

    for query in demo_queries:
        result = pipeline.run(query)
        results.append(result)

        print("=" * 80)
        print(f"Query: {query}")
        print("-" * 80)
        print(result["answer"])
        print()

    output_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"saved: {output_path}")

    print("[Top-5 Search Results]")
    for idx, item in enumerate(result["search_results"][:5], start=1):
        print(
            idx,
            item.get("project_id"),
            item.get("title"),
            "score=", item.get("score"),
            "emb=", item.get("embedding_score"),
            "meta=", item.get("metadata_score"),
            "reason=", item.get("explanation"),
        )
    print()
    print("[RAG Answer]")
    print(result["answer"])


if __name__ == "__main__":
    main()