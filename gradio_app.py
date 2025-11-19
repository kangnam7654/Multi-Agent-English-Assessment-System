# gradio_app.py
import json
from typing import Any

import gradio as gr
from langchain_ollama import ChatOllama

from agents.state import AgentState, Grade, Level, Mode
from workflow_builder import build_workflow

# 전역 리소스
llm = ChatOllama(model="gpt-oss:20b", temperature=0)
graph, context_state = build_workflow(llm)


def run_pipeline(
    mode: str,
    user_prompt,
    grade_for_student: str,
    grade_for_assessor: str,
    level: str,
    essay_input: str,
):
    # 타입 캐스팅 (문자열 → Literal)
    mode_t: Mode = mode  # type: ignore[assignment]
    grade_for_student_t: Grade = grade_for_student  # type: ignore[assignment]
    grade_for_assessor_t: Grade = grade_for_assessor  # type: ignore[assignment]
    level_t: Level = level  # type: ignore[assignment]

    initial_state: AgentState = {
        "system_prompt": None,
        "user_prompt": user_prompt,
        "essay": essay_input,
        "assessed_content": None,
        "grade_for_student": grade_for_student_t,
        "grade_for_assessor": grade_for_assessor_t,
        "level": level_t,
        "mode": mode_t,
        "next_agent": None,
    }

    final_state = graph.invoke(initial_state, context=context_state)

    essay_out = final_state.get("essay")
    assessed_content = final_state.get("assessed_content")

    # AgentAssessor 는 dict 를 직접 넣으므로 유형별로 안전하게 파싱
    assessed_json: dict[str, Any] | None = None
    if isinstance(assessed_content, dict):
        assessed_json = assessed_content
    elif isinstance(assessed_content, str):
        try:
            assessed_json = json.loads(assessed_content)
        except json.JSONDecodeError:
            assessed_json = {"raw": assessed_content}
            print("Assessed content is not valid JSON, returning raw string.")
    return essay_out, assessed_json


def build_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# English Writing Agent (Student + Assessor)")

        with gr.Row():
            mode = gr.Radio(
                ["synthesis", "assessment"],
                value="synthesis",
                label="Mode",
                info="synthesis: generate + assess, assessment: assess my essay",
            )
            grade_for_assessor = gr.Dropdown(
                ["elem_6", "mid_2", "high_2"],
                value="mid_2",
                label="Grade for Assessor",
            )
            grade_for_student = gr.Dropdown(
                ["elem_6", "mid_2", "high_2"],
                value="mid_2",
                label="Grade for Student",
            )
            level = gr.Dropdown(
                ["beginner", "intermediate", "advanced", "master"],
                value="intermediate",
                label="Level (used in synthesis mode)",
            )
        with gr.Row():
            user_prompt = gr.Textbox(
                label="User Prompt (used only in synthesis mode)",
                lines=4,
                placeholder="Enter the essay topic or instructions here.",
            )

            essay_input = gr.Textbox(
                label="Your Essay (used only in assessment mode)",
                lines=4,
                placeholder="Paste your English essay here if you choose 'assessment' mode.",
            )

        run_btn = gr.Button("Run")

        essay_output = gr.Textbox(
            label="Generated / Evaluated Essay (final essay in state['essay'])",
            lines=10,
        )
        assessed_output = gr.JSON(
            label="Assessment Result (JSON)",
        )

        def _on_run(m, u, g_s, g_a, level_value, e):
            return run_pipeline(m, u, g_s, g_a, level_value, e)

        run_btn.click(
            _on_run,
            inputs=[
                mode,
                user_prompt,
                grade_for_student,
                grade_for_assessor,
                level,
                essay_input,
            ],
            outputs=[essay_output, assessed_output],
        )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch()
