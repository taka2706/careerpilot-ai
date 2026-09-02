"""OpenAI Responses API abstraction with bounded retries and usage tracking."""

from typing import Protocol, TypeVar

from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError
from pydantic import BaseModel
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings

StructuredOutput = TypeVar("StructuredOutput", bound=BaseModel)


class StructuredLLM(Protocol):
    """Minimal contract used by agents that request validated model output."""

    @property
    def total_tokens(self) -> int: ...

    def generate(
        self,
        *,
        instructions: str,
        input_text: str,
        response_model: type[StructuredOutput],
    ) -> StructuredOutput: ...


class LLMUnavailableError(RuntimeError):
    """Raised when configured model generation cannot produce validated output."""


class OpenAIResponsesLLM:
    """Validated structured generation through the current OpenAI Responses API."""

    def __init__(self, settings: Settings) -> None:
        if (
            settings.openai_api_key is None
            or not settings.openai_api_key.get_secret_value().strip()
            or not settings.openai_model
        ):
            raise LLMUnavailableError("OPENAI_API_KEY and OPENAI_MODEL are required for LLM mode.")
        api_key = settings.openai_api_key.get_secret_value()
        if settings.openai_base_url:
            self._client = OpenAI(
                api_key=api_key,
                base_url=settings.openai_base_url,
                timeout=settings.llm_timeout_seconds,
            )
        else:
            self._client = OpenAI(api_key=api_key, timeout=settings.llm_timeout_seconds)
        self._model = settings.openai_model
        self._max_retries = settings.max_agent_retries
        self._total_tokens = 0

    @property
    def total_tokens(self) -> int:
        return self._total_tokens

    def generate(
        self,
        *,
        instructions: str,
        input_text: str,
        response_model: type[StructuredOutput],
    ) -> StructuredOutput:
        retrying = Retrying(
            stop=stop_after_attempt(self._max_retries + 1),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
            retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIConnectionError)),
            reraise=True,
        )
        for attempt in retrying:
            with attempt:
                response = self._client.responses.parse(
                    model=self._model,
                    instructions=instructions,
                    input=input_text,
                    text_format=response_model,
                    max_output_tokens=2_000,
                    store=False,
                )
                if response.usage:
                    self._total_tokens += response.usage.total_tokens
                if response.output_parsed is None:
                    raise LLMUnavailableError("The model returned no validated structured output.")
                return response.output_parsed
        raise LLMUnavailableError("The model request did not complete.")


def create_llm(settings: Settings) -> StructuredLLM | None:
    """Return an optional client; local deterministic behavior remains the default."""

    if (
        settings.openai_api_key is None
        or not settings.openai_api_key.get_secret_value().strip()
        or not settings.openai_model
    ):
        return None
    return OpenAIResponsesLLM(settings)
