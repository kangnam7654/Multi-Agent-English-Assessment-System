# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-Agent English Assessment System using LangGraph. Three agents (Orchestrator → Student → Assessor) generate and evaluate English essays via a local Ollama LLM (`gpt-oss:20b`). Two modes: "synthesis" (generate + assess) and "assessment" (assess only).

## Commands

```bash
# Install backend dependencies
uv sync

# Run FastAPI server (POST /run endpoint)
uv run uvicorn app:app --reload --port 8000

# Run React frontend (http://localhost:3000)
cd frontend && npm install && npm run dev
```

No tests exist in this project.

## Architecture

**Workflow (LangGraph StateGraph):**
`orchestrator` → `student` (if synthesis mode) → `orchestrator` → `assessor` → END

- `workflow_builder.py` — Builds the LangGraph state machine with conditional routing via `router_fn`
- `agents/state.py` — `AgentState` and `ContextState` TypedDicts; defines `Grade`, `Level`, `Mode` literals
- `agents/base.py` — `BaseAgent` base class; all agents implement `__call__(state, runtime)`, LLM accessed via `runtime.context`
- `agents/orchestrator.py` — Routes by mode, builds system prompts using `SystemPromptBuilder`
- `agents/student.py` — Generates essay as JSON (`{grade, level, essay_english, word_count}`)
- `agents/assessor.py` — Evaluates essay as JSON (`{grade, overall_score, level, per_criterion, feedback_english, feedback_korean}`)
- `prompts/builder.py` — `SystemPromptBuilder` loads rubric and fills `.md` templates with grade/level context
- `prompts/rubric/rubric.json` — Rubric definitions: 3 grades × 4 proficiency levels × 5 criteria
- `prompts/system_prompts/` — Markdown prompt templates for student and assessor

- `config.py` — Shared LLM/workflow factory (`create_graph`, `create_initial_state`); model config (`LLM_MODEL`, `LLM_TEMPERATURE`)

**Frontend:** `frontend/` — Next.js (React) app with Tailwind CSS. Calls FastAPI `POST /run` endpoint.

**Entry points:** `app.py` (FastAPI backend) serves the API. `frontend/` (React) provides the web UI.

## Conventions

- Agents return partial state dicts to update the shared `AgentState` TypedDict
- LLM outputs are expected as JSON; `BaseAgent.parse_json()` provides shared fallback extraction
- Prompt templates use Python `str.format()` with rubric data injected at runtime
- `ChatOllama` is configured with `temperature=0` for deterministic output
- FastAPI has CORS enabled for `localhost:3000` (React dev server)
