# agents/student.py
import json
from json import JSONDecodeError

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from agents.base import BaseAgent
from agents.state import AgentState, ContextState


class AgentStudent(BaseAgent):
    """
    - Orchestrator가 넣어준 system_prompt 를 사용해
    - 해당 grade/level 수준의 에세이를 생성하는 에이전트.

    기대 LLM Output(JSON):
    {
      "grade": "elem_6" | "mid_2" | "high_2",
      "level": "beginner" | "intermediate" | "advanced" | "master",
      "essay_english": "<essay text>",
      "word_count": 123
    }
    """

    def __call__(self, state: AgentState, runtime: Runtime[ContextState]) -> AgentState:
        llm = runtime.context["llm"]

        system_prompt = state.get("system_prompt") or ""
        user_prompt = state.get("user_prompt") or ""
        if not system_prompt:
            raise ValueError("system_prompt is missing in state for AgentStudent.")

        # Student에서는 별도의 user_prompt 없이, system_prompt가 모든 규칙을 포함
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),  # 트리거용 간단 메시지
        ]

        llm_result = llm.invoke(messages)

        try:
            result = json.loads(llm_result.content)
        except JSONDecodeError:
            result = self._parse_result(llm_result.content)

        essay = result.get("essay_english", "")
        if not essay:
            raise ValueError("LLM result does not contain 'essay_english'.")

        state["essay"] = essay

        # 이 상태에서 mode를 바로 assessment로 바꿔 평가로 넘길 수도 있음 (옵션)
        state["mode"] = "assessment"
        # state["next_agent"] = "assessor"

        return state

    def _parse_result(self, llm_result: str) -> dict:
        text = llm_result.strip()
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1
        if start_idx == -1 or end_idx <= start_idx:
            raise ValueError("No JSON object found in LLM result (Student).")
        json_str = text[start_idx:end_idx]
        return json.loads(json_str)
