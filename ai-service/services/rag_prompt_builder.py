from __future__ import annotations


def build_rag_prompt(query: str, contexts: list[dict]) -> str:
    context_text = "\n\n".join(item["context_text"] for item in contexts)

    ranked_list = "\n".join(
        [
            f"{item['rank']}위: {item['title']} ({item['project_id']}) "
            f"/ score={item.get('score')} / reason={item.get('explanation')}"
            for item in contexts
        ]
    )

    top_context = contexts[0] if contexts else None
    top_project_line = ""
    if top_context:
        top_project_line = (
            f"검색 시스템이 판단한 1순위 프로젝트는 "
            f"{top_context['title']} ({top_context['project_id']})이다."
        )

    return f"""
너는 교내 프로젝트 아카이브 검색 도우미다.

중요 규칙:
1. 반드시 아래 검색 결과 context에 적힌 정보만 사용한다.
2. context에 없는 기술, 기능, 설명은 절대 추가하지 않는다.
3. 검색 시스템의 순위를 임의로 바꾸지 않는다.
4. 반드시 검색순위 1번 프로젝트를 '가장 적합한 프로젝트'로 먼저 설명한다.
5. 추가 후보는 검색순위 2번, 3번 순서대로 설명한다.
6. 질문과 관련성이 낮은 후보는 "추가 후보이지만 직접 관련성은 낮다"고 말한다.
7. 프로젝트명은 반드시 context의 title 또는 project_id를 그대로 사용한다.
8. 한국어로 답변한다.

사용자 질문:
{query}

검색 시스템 판단:
{top_project_line}

검색 순위 요약:
{ranked_list}

검색 결과 context:
{context_text}

답변 형식:
1. 가장 적합한 프로젝트
- 프로젝트명:
- 추천 이유:
- 근거가 되는 context 정보:

2. 추가로 볼 만한 프로젝트
- 프로젝트명:
- 추천 이유:
- 관련성 판단:

3. 추천 순위 요약
- 1순위:
- 2순위:
- 3순위:
""".strip()