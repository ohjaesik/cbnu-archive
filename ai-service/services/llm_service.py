from __future__ import annotations

from typing import Any, Dict, List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class LocalLLMService:
    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-7B-Instruct",
        max_new_tokens: int = 400,
    ):
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
            trust_remote_code=True,
        )

    def build_prompt(self, query: str, ranked_projects: List[Dict[str, Any]]) -> str:
        if not ranked_projects:
            return f"""
사용자 질문:
{query}

검색 결과가 없습니다.
질문에 대해 관련 프로젝트를 찾지 못했다고 한국어로 설명하세요.
""".strip()

        project_blocks = []
        for item in ranked_projects:
            block = f"""
순위: {item.get("rank")}
프로젝트명: {item.get("title")}
주제: {item.get("topic")}
기술 스택: {", ".join(item.get("tech_stack", []))}
난이도: {item.get("difficulty")}
프로젝트 유형: {item.get("project_type")}
추천 이유: {", ".join(item.get("reasons", []))}
유사도 점수: {item.get("final_score")}
""".strip()
            project_blocks.append(block)

        context = "\n\n".join(project_blocks)

        prompt = f"""
당신은 교내 프로젝트 아카이브 추천 도우미입니다.
반드시 아래 검색 결과만 근거로 답변하세요.
없는 내용을 지어내지 마세요.

사용자 질문:
{query}

검색 결과:
{context}

답변 형식:
1. 질문에 가장 적합한 프로젝트를 먼저 추천
2. 각 프로젝트별 추천 이유를 짧게 설명
3. 마지막에 "추천 순위 요약"을 1~3위 중심으로 정리
4. 한국어로 자연스럽게 답변
""".strip()

        return prompt

    def generate_answer(self, query: str, ranked_projects: List[Dict[str, Any]]) -> str:
        prompt = self.build_prompt(query, ranked_projects)

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                temperature=0.0,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # 프롬프트까지 포함되어 디코딩될 수 있으므로, 뒤쪽 답변만 잘라내기
        if prompt in generated_text:
            generated_text = generated_text[len(prompt):].strip()

        return generated_text