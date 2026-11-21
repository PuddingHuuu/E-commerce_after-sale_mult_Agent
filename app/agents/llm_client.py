import json
import re
import time
from dataclasses import dataclass
from typing import Any

from app.core.config import settings


@dataclass
class LLMResult:
    data: dict[str, Any]
    model: str
    prompt_tokens: int | None
    completion_tokens: int | None
    duration_ms: int


class LLMClient:
    """Small OpenAI-compatible client. DeepSeek is the default provider."""

    def __init__(self) -> None:
        self._client = None
        self.model = settings.llm_model

    @property
    def available(self) -> bool:
        return bool(settings.llm_api_key.strip())

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
                timeout=settings.llm_timeout_seconds,
                max_retries=settings.llm_max_retries,
            )
        return self._client

    @staticmethod
    def _extract_json(content: str) -> dict[str, Any]:
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end < start:
            raise ValueError("模型未返回 JSON 对象")
        data = json.loads(text[start : end + 1])
        if not isinstance(data, dict):
            raise ValueError("模型返回的 JSON 不是对象")
        return data

    def chat_json(self, system_prompt: str, user_prompt: str) -> LLMResult:
        if not self.available:
            raise RuntimeError("未配置 LLM_API_KEY")

        started = time.perf_counter()
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens,
        }
        if settings.llm_json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self._get_client().chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        return LLMResult(
            data=self._extract_json(content),
            model=response.model or self.model,
            prompt_tokens=getattr(usage, "prompt_tokens", None) if usage else None,
            completion_tokens=getattr(usage, "completion_tokens", None) if usage else None,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )


llm_client = LLMClient()
