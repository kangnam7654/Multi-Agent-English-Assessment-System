# Multi Agent English Assessment System

[![한국어](https://img.shields.io/badge/lang-한국어-blue)](README.ko.md)

> Portfolio project — a simplified reconstruction of an English writing assessment system I previously operated in production.

## Overview

A multi-agent system that **generates and evaluates** English essays. Built on LangGraph with three agents (Orchestrator / Student / Assessor), it writes grade- and level-appropriate essays and evaluates them against a rubric.

- All LLM calls go through **Ollama + langchain-ollama**, using the free local model `gpt-oss:20b` by default.
- No cloud API dependencies — runs entirely on your machine.

## Key Features

- Automatic English essay generation (Student agent)
- Rubric-based essay evaluation (Assessor agent)
- Mode/grade/level-aware workflow routing (Orchestrator)
- FastAPI `/run` HTTP endpoint
- Gradio web UI demo (`gradio_app.py`)

## Architecture

![English Writing Multi-Agent Architecture](docs/architecture.drawio.png)

**Workflow (LangGraph StateGraph):**

`orchestrator` → `student` (synthesis mode) → `orchestrator` → `assessor` → END

1. Client sends a request via `/run` API or Gradio UI.
2. **Orchestrator** inspects `mode` / `essay` / `grade` / `level` and determines the next agent + system prompt.
3. **Student** or **Assessor** calls the LLM (Ollama) and produces a JSON result.
4. The final assessment (and generated essay, if applicable) is returned in `AgentState`.

### Sequence Diagram

![Sequence Diagram](docs/sequence_diagram.png)

- Source: `docs/sequence_diagram.puml` (PlantUML)
- Architecture diagram: `docs/architecture.drawio` (open with draw.io)

## Tech Stack

- Python 3.12
- FastAPI / Gradio
- LangGraph / LangChain + langchain-ollama
- Ollama (`gpt-oss:20b`)

## Getting Started

### Prerequisites

1. Python >= 3.12
2. [Ollama](https://ollama.com/) installed and running
   ```bash
   ollama serve
   ollama pull gpt-oss:20b
   ```
3. (Recommended) [uv](https://github.com/astral-sh/uv) — this project is set up with uv.

### Install Dependencies

```bash
# uv (recommended)
uv sync

# or plain venv + pip
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install fastapi gradio langchain-core langchain-ollama langgraph pyyaml uvicorn
```

### Run FastAPI Server

```bash
uv run uvicorn app:app --reload --port 8000
```

Endpoint: `POST http://127.0.0.1:8000/run`

Request example:

```json
{
  "mode": "synthesis",
  "user_prompt": "Write an essay about studying computer science as a hobby.",
  "grade_for_student": "mid_2",
  "grade_for_assessor": "mid_2",
  "level": "intermediate",
  "essay": null
}
```

Response fields: `grade`, `level`, `essay`, `assessed_content`

### Run Gradio Web UI

```bash
uv run python gradio_app.py
```

Open `http://127.0.0.1:7860`

- **synthesis** mode: enter a topic → Student generates an essay → Assessor evaluates it.
- **assessment** mode: paste your essay → Assessor evaluates it.

## Why Ollama?

Ollama enables free, local LLM experimentation without cloud API costs. The default model is `gpt-oss:20b`, but you can swap it for any model installed in Ollama by changing `LLM_MODEL` in `config.py`.

## Portfolio Highlights

- Multi-agent architecture (Orchestrator + Student + Assessor) implemented with LangGraph
- English education domain expertise — grade/level rubric design and LLM prompt engineering
- Zero cloud dependency — local Ollama model
- End-to-end demo with FastAPI backend + Gradio UI
- Safely reconstructed from a real production project (no proprietary code or data)

## Limitations

- This is a **portfolio / research** project, not production-ready.
- Local LLM quality depends on the model used.

## License

[MIT License](LICENSE)
