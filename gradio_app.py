# gradio_app.py
import json
from typing import Any

import gradio as gr

from config import create_graph, create_initial_state

graph, context_state = create_graph()


def run_pipeline(
    mode: str,
    user_prompt: str,
    grade_for_student: str,
    grade_for_assessor: str,
    level: str,
    essay_input: str,
):
    initial_state = create_initial_state(
        mode=mode,  # type: ignore[arg-type]
        user_prompt=user_prompt,
        grade_for_student=grade_for_student,  # type: ignore[arg-type]
        grade_for_assessor=grade_for_assessor,  # type: ignore[arg-type]
        level=level,  # type: ignore[arg-type]
        essay=essay_input,
    )

    final_state = graph.invoke(initial_state, context=context_state)

    essay_out = final_state.get("essay")
    assessed_content = final_state.get("assessed_content")

    assessed_json: dict[str, Any] | None = None
    if isinstance(assessed_content, dict):
        assessed_json = assessed_content
    elif isinstance(assessed_content, str):
        try:
            assessed_json = json.loads(assessed_content)
        except json.JSONDecodeError:
            assessed_json = {"raw": assessed_content}

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

        run_btn.click(
            run_pipeline,
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
