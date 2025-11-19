# agents/assessor.py
import json
from json import JSONDecodeError

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from agents.base import BaseAgent
from agents.state import AgentState, ContextState


class AgentAssessor(BaseAgent):
    """
    - Orchestrator가 넣어준 Assessor system_prompt 를 사용해
    - state["essay"] 를 평가하는 에이전트.

    기대 LLM Output(JSON):
    {
      "grade": "...",
      "overall_score": number,
      "level": "beginner" | "intermediate" | "advanced" | "master",
      "per_criterion": { ... },
      "summary_feedback_english": "...",
      "summary_feedback_korean": "..."
    }
    """

    def __call__(self, state: AgentState, runtime: Runtime[ContextState]) -> AgentState:
        llm = runtime.context["llm"]

        system_prompt = state.get("system_prompt") or ""
        if not system_prompt:
            raise ValueError("system_prompt is missing in state for AgentAssessor.")

        essay = state.get("essay") or ""
        if not essay:
            raise ValueError("No essay found in state['essay'] for AgentAssessor.")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=essay),
        ]

        llm_result = llm.invoke(messages)

        try:
            result = json.loads(llm_result.content)
        except JSONDecodeError:
            result = self._parse_result(llm_result.content)

        state["assessed_content"] = result

        # 필요 시 편의 필드도 추가할 수 있음 (TypedDict에는 없지만 런타임에서 사용 가능)
        if "overall_score" in result:
            state["overall_score"] = result["overall_score"]  # type: ignore[index]
        return state

    def _parse_result(self, llm_result: str) -> dict:
        text = llm_result.strip()
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1
        if start_idx == -1 or end_idx <= start_idx:
            raise ValueError("No JSON object found in LLM result (Assessor).")
        json_str = text[start_idx:end_idx]
        return json.loads(json_str)
