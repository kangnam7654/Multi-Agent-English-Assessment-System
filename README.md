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
- React (Next.js) web frontend

## Architecture

![English Writing Multi-Agent Architecture](docs/architecture.drawio.png)

**Workflow (LangGraph StateGraph):**

`orchestrator` → `student` (synthesis mode) → `orchestrator` → `assessor` → END

1. Client sends a request via `/run` API or the React frontend.
2. **Orchestrator** inspects `mode` / `essay` / `grade` / `level` and determines the next agent + system prompt.
3. **Student** or **Assessor** calls the LLM (Ollama) and produces a JSON result.
4. The final assessment (and generated essay, if applicable) is returned in `AgentState`.

### Sequence Diagram

![Sequence Diagram](docs/sequence_diagram.png)

- Source: `docs/sequence_diagram.puml` (PlantUML)
- Architecture diagram: `docs/architecture.drawio` (open with draw.io)

## Tech Stack

- Python 3.12
- FastAPI (backend API)
- Next.js / React / Tailwind CSS (frontend)
- LangGraph / LangChain + langchain-ollama
- Ollama (`gpt-oss:20b`)

## Getting Started

### Prerequisites

1. Python >= 3.12
2. Node.js >= 18 (for the React frontend)
3. [Ollama](https://ollama.com/) installed and running
   ```bash
   ollama serve
   ollama pull gpt-oss:20b
   ```
4. (Recommended) [uv](https://github.com/astral-sh/uv) — this project is set up with uv.

### Install Dependencies

```bash
# Backend (uv recommended)
uv sync

# Frontend
cd frontend && npm install
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

### Run React Frontend

```bash
cd frontend && npm run dev
```

Open `http://localhost:3000`

- **synthesis** mode: enter a topic → Student generates an essay → Assessor evaluates it.
- **assessment** mode: paste your essay → Assessor evaluates it.

### Environment Variables (optional)

| Variable | Default | Description |
|---|---|---|
| `LLM_MODEL` | `gpt-oss:20b` | Ollama model name |
| `LLM_TEMPERATURE` | `0` | LLM temperature |
| `LLM_BASE_URL` | `http://localhost:11434` | Ollama API base URL |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | FastAPI URL for frontend |

## Why Ollama?

Ollama enables free, local LLM experimentation without cloud API costs. The default model is `gpt-oss:20b`, but you can swap it for any model installed in Ollama by setting the `LLM_MODEL` environment variable.

## Portfolio Highlights

- Multi-agent architecture (Orchestrator + Student + Assessor) implemented with LangGraph
- English education domain expertise — grade/level rubric design and LLM prompt engineering
- Zero cloud dependency — local Ollama model
- End-to-end demo with FastAPI backend + React frontend
- Safely reconstructed from a real production project (no proprietary code or data)

## Limitations

- This is a **portfolio / research** project, not production-ready.
- Local LLM quality depends on the model used.

## License

[MIT License](LICENSE)
