import json
import logging
import re
import time
from json import JSONDecodeError

from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langgraph.runtime import Runtime

from agents.state import AgentState, ContextState

logger = logging.getLogger(__name__)

MAX_LLM_RETRIES = 2
RETRY_DELAY_SECONDS = 1


class BaseAgent:
    """Base class for all agents."""

    def __call__(self, state: AgentState, runtime: Runtime[ContextState]) -> AgentState:
        raise NotImplementedError

    @staticmethod
    def invoke_llm_with_retry(
        llm: ChatOllama,
        messages: list[BaseMessage],
        agent_label: str = "Agent",
    ) -> str:
        """LLM을 호출하고, 실패 시 재시도한다. 최종 응답 텍스트를 반환."""
        last_error: Exception | None = None
        for attempt in range(1 + MAX_LLM_RETRIES):
            try:
                result = llm.invoke(messages)
                return result.content
            except Exception as e:
                last_error = e
                if attempt < MAX_LLM_RETRIES:
                    delay = RETRY_DELAY_SECONDS * (2 ** attempt)
                    logger.warning(
                        "[%s] LLM call failed (attempt %d/%d): %s — retrying in %ds",
                        agent_label, attempt + 1, 1 + MAX_LLM_RETRIES, e, delay,
                    )
                    time.sleep(delay)
        raise RuntimeError(
            f"[{agent_label}] LLM call failed after {1 + MAX_LLM_RETRIES} attempts: {last_error}"
        )

    @staticmethod
    def parse_json(raw: str, agent_label: str = "Agent") -> dict:
        """LLM 응답에서 JSON을 파싱한다. 코드펜스, 앞뒤 텍스트를 처리."""
        text = raw.strip()

        # 1차: 그대로 파싱
        try:
            return json.loads(text)
        except JSONDecodeError:
            pass

        # 2차: ```json ... ``` 코드펜스 추출
        fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
        if fence_match:
            try:
                return json.loads(fence_match.group(1).strip())
            except JSONDecodeError:
                pass

        # 3차: 가장 바깥 { ... } 블록 추출 (중첩 브레이스 고려)
        start = text.find("{")
        if start == -1:
            raise ValueError(f"No JSON object found in LLM result ({agent_label}).")

        depth = 0
        end = -1
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        if end <= start:
            raise ValueError(f"Unbalanced braces in LLM result ({agent_label}).")

        candidate = text[start:end]
        try:
            parsed = json.loads(candidate)
            logger.info("[%s] JSON extracted via fallback brace matching", agent_label)
            return parsed
        except JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON from LLM result ({agent_label}): {e}"
            ) from e
