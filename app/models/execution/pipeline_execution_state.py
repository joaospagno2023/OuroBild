"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_execution_state.py
Descrição : Estado atual de uma execução da Pipeline.
--------------------------------------------------------------------
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class PipelineExecutionStatus(str, Enum):
    """
    Status geral da execução da Pipeline.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineExecutionPhase(str, Enum):
    """
    Fase atual da execução.
    """

    PIPELINE = "pipeline"
    SETUP = "setup"


class PipelineExecutionState(BaseModel):
    """
    Representa o estado atual de uma execução.
    """

    execution_id: str
    project_id: str

    status: PipelineExecutionStatus = (
        PipelineExecutionStatus.PENDING
    )

    phase: PipelineExecutionPhase = (
        PipelineExecutionPhase.PIPELINE
    )

    current_step: str | None = None
    current_step_index: int = 0
    total_steps: int = 0
    progress_percent: int = 0

    message: str = ""

    started_at: datetime | None = None
    finished_at: datetime | None = None

    elapsed_seconds: float = 0.0

    success: bool | None = None
    failed_step: str | None = None