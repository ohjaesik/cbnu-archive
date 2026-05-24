from __future__ import annotations

import os
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class LocalLLMAnswerService:
    def __init__(
        self,
        model_name: str | None = None,
        max_new_tokens: int = 500,
    ):
        self.model_name = model_name or os.getenv(
            "LOCAL_LLM_MODEL",
            "Qwen/Qwen2.5-0.5B-Instruct",
        )
        self.max_new_tokens = max_new_tokens

        print(f"[LocalLLMAnswerService] loading model: {self.model_name}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
        )

        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=dtype,
            device_map="auto",
            trust_remote_code=True,
        )

        self.model.eval()

    def _build_chat_input(self, prompt: str) -> dict[str, Any]:
        messages = [
            {
                "role": "system",
                "content": "너는 교내 프로젝트 아카이브의 근거 기반 추천 도우미다.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        if hasattr(self.tokenizer, "apply_chat_template"):
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            text = prompt

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
        )

        return {k: v.to(self.model.device) for k, v in inputs.items()}

    def generate(
        self,
        query: str,
        prompt: str,
        contexts: list[dict[str, Any]],
    ) -> str:
        if not contexts:
            return (
                "검색 결과를 찾지 못했습니다. "
                "질의를 더 구체적으로 입력하거나 기술 스택, 주제, 키워드를 포함해 다시 검색해보세요."
            )

        inputs = self._build_chat_input(prompt)
        input_length = inputs["input_ids"].shape[-1]

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated_ids = outputs[0][input_length:]
        answer = self.tokenizer.decode(
            generated_ids,
            skip_special_tokens=True,
        )

        return answer.strip()