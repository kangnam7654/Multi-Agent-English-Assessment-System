# app.py
import asyncio
import logging
import time
import uuid
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, model_validator

from agents.state import Grade, Level, Mode
from config import create_graph, create_initial_state

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

PIPELINE_TIMEOUT_SECONDS = 300  # 5 minutes

graph, context_state = create_graph()


class RunRequest(BaseModel):
    mode: Mode = "synthesis"
    user_prompt: Optional[str] = None
    grade_for_student: Grade = "mid_2"
    grade_for_assessor: Grade = "mid_2"
    level: Level = "intermediate"
    essay: Optional[str] = None

    @model_validator(mode="after")
    def validate_mode_fields(self):
        if self.mode == "synthesis":
            if not self.user_prompt or not self.user_prompt.strip():
                raise ValueError("user_prompt is required for synthesis mode.")
        elif self.mode == "assessment":
            if not self.essay or not self.essay.strip():
                raise ValueError("essay is required for assessment mode.")
        return self


class RunResponse(BaseModel):
    grade: Optional[Grade] = None
    level: Optional[Level] = None
    essay: Optional[str] = None
    assessed_content: Optional[dict[str, Any]] = None


app = FastAPI(title="English Assessment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.post("/run", response_model=RunResponse)
async def run_agent(req: RunRequest):
    request_id = uuid.uuid4().hex[:8]
    logger.info(
        "[%s] mode=%s grade_student=%s grade_assessor=%s level=%s",
        request_id, req.mode, req.grade_for_student, req.grade_for_assessor, req.level,
    )
    start = time.monotonic()

    try:
        initial_state = create_initial_state(
            mode=req.mode,
            user_prompt=req.user_prompt,
            grade_for_student=req.grade_for_student,
            grade_for_assessor=req.grade_for_assessor,
            level=req.level,
            essay=req.essay,
        )

        final_state = await asyncio.wait_for(
            asyncio.to_thread(graph.invoke, initial_state, context=context_state),
            timeout=PIPELINE_TIMEOUT_SECONDS,
        )

        elapsed = time.monotonic() - start
        logger.info("[%s] completed in %.1fs", request_id, elapsed)

        return RunResponse(
            grade=final_state.get("grade"),
            level=final_state.get("level"),
            essay=final_state.get("essay"),
            assessed_content=final_state.get("assessed_content"),
        )
    except TimeoutError:
        elapsed = time.monotonic() - start
        logger.error("[%s] timed out after %.1fs", request_id, elapsed)
        raise HTTPException(status_code=504, detail="Pipeline timed out.")
    except ValueError as e:
        logger.warning("[%s] validation error: %s", request_id, e)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        elapsed = time.monotonic() - start
        logger.exception("[%s] failed after %.1fs", request_id, elapsed)
        raise HTTPException(status_code=500, detail="Pipeline execution failed. Check server logs for details.")
