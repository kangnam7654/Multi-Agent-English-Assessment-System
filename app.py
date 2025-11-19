# app.py
from typing import Optional

from fastapi import FastAPI
from langchain_ollama import ChatOllama
from pydantic import BaseModel
from workflow_builder import build_workflow

from agents.state import AgentState, Grade, Level, Mode

# 1) 전역으로 LLM & Workflow 준비 (프로세스 시작 시 1번만)
llm = ChatOllama(model="gpt-oss:20b", temperature=0)
graph, context_state = build_workflow(llm)


# 2) 요청 바디 스키마 정의
class RunRequest(BaseModel):
    mode: Mode = "synthesis"  # "synthesis" or "assessment"
    user_prompt: Optional[str] = "컴퓨터 코딩에 대한 취미생활인 삶에 대해 에세이를 써줘."  # synthesis 시 사용
    grade_for_student: Grade = "mid_2"
    grade_for_assessor: Grade = "mid_2"
    level: Level = "intermediate"  # synthesis 시 사용, assessment-only일 때는 무시 가능
    essay: Optional[str] = None  # assessment-only 모드에서 유저가 넣는 에세이


class RunResponse(BaseModel):
    grade: Optional[Grade]
    level: Optional[Level]
    essay: Optional[str]
    assessed_content: Optional[str]


app = FastAPI()


@app.post("/run", response_model=RunResponse)
def run_agent(req: RunRequest):
    # 3) 초기 state 구성
    initial_state: AgentState = {
        "system_prompt": None,
        "user_prompt": None,
        "essay": req.essay if req.mode == "assessment" else None,
        "assessed_content": None,
        "grade_for_student": req.grade_for_student,
        "grade_for_assessor": req.grade_for_assessor,
        "level": req.level,
        "mode": req.mode,
        "next_agent": None,
    }

    final_state = graph.invoke(initial_state, context=context_state)

    return RunResponse(
        grade=final_state.get("grade"),
        level=final_state.get("level"),
        essay=final_state.get("essay"),
        assessed_content=final_state.get("assessed_content"),
    )
