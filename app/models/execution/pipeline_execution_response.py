"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_execution_response.py
Descrição : Resposta da consulta de execução da Pipeline.
--------------------------------------------------------------------
"""

from datetime import datetime

from pydantic import BaseModel

from app.models.execution.pipeline_execution_state import (
    PipelineExecutionPhase,
    PipelineExecutionStatus,
)


class PipelineExecutionResponse(BaseModel):
    """
    Representa a resposta da API para uma execução.
    """

    execution_id: str
    project_id: str

    status: PipelineExecutionStatus
    phase: PipelineExecutionPhase

    current_step: str | None
    current_step_index: int
    total_steps: int
    progress_percent: int

    message: str

    started_at: datetime | None
    finished_at: datetime | None

    elapsed_seconds: float

    success: bool | None
    failed_step: str | None