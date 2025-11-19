from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from agents.state import AgentState, ContextState


class BaseAgent:
    """Base class for all agents."""

    def __init__(self):
        pass

    def __call__(self, state: AgentState, runtime: Runtime[ContextState]) -> AgentState:
        llm = runtime.context["llm"]
        system_prompt = state.get("system_prompt", "")
        user_prompt = state.get("user_prompt", "")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        result = llm.invoke(messages)
        if state.get("verbose", False):
            print("=" * 80)
            print("📤 LLM 원본 응답:")
            print("=" * 80)
            print(result.content)
            print("\n" + "=" * 80)
        return state
