"""Adapter gọi Google Gemini API qua SDK `google-genai` với Structured Output.

Tuân thủ quy ước:
1. Import SDK LLM bên trong adapter ở tầng `src/llm`.
2. Kiểm tra an toàn `assert_no_egress(prompt)` trước khi gửi dữ liệu ra mạng.
3. Fallback an toàn về ScriptedGateway khi ở chế độ offline hoặc thiếu API key.
"""

from __future__ import annotations

import json
import logging
from typing import TypeVar

from pydantic import BaseModel

from src.llm.gateway import LLMGateway, LLMUnavailableError
from src.llm.safety import assert_no_egress
from src.llm.settings import LLMSettings, get_llm_settings

logger = logging.getLogger(__name__)
SchemaT = TypeVar("SchemaT", bound=BaseModel)


class GeminiGateway(LLMGateway):
    """Adapter kết nối Gemini API trả về Structured Output theo Pydantic schema."""

    def __init__(self, settings: LLMSettings | None = None) -> None:
        self.settings = settings or get_llm_settings()
        self._client = None
        key = self.settings.api_key.get_secret_value()
        if key:
            try:
                from google import genai

                self._client = genai.Client(api_key=key)
            except (ImportError, RuntimeError, ValueError) as e:
                logger.warning("Không thể khởi tạo Google GenAI Client: %s", e)

    def select(self, prompt: str, schema: type[SchemaT]) -> SchemaT:
        """Gửi prompt tới Gemini và ép kiểu trả về đúng `schema`."""
        assert_no_egress(prompt)

        if not self._client:
            raise LLMUnavailableError("Gemini Client chưa được cấu hình API Key hợp lệ.")

        model_name = self.settings.model or "gemini-2.5-flash"
        for attempt in range(self.settings.max_attempts):
            try:
                response = self._client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": schema,
                    },
                )
                text = response.text or ""
                payload = json.loads(text)
                return schema.model_validate(payload)
            except Exception as err:
                logger.warning("Lỗi gọi Gemini lần %d/%d: %s", attempt + 1, self.settings.max_attempts, err)
                if attempt + 1 == self.settings.max_attempts:
                    raise LLMUnavailableError(f"Gemini không trả về kết quả hợp lệ: {err}") from err

        raise LLMUnavailableError("Hết lượt thử gọi Gemini.")


def create_llm_gateway(settings: LLMSettings | None = None) -> LLMGateway:
    """Factory tạo gateway phù hợp cấu hình."""
    cfg = settings or get_llm_settings()
    if cfg.provider == "gemini" and cfg.api_key.get_secret_value():
        return GeminiGateway(cfg)
    # Mặc định offline
    from src.llm.gateway import ScriptedGateway

    return ScriptedGateway([])
