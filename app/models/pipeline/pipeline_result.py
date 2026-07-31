"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_result.py
Descrição : Resultado final da execução da Pipeline.
--------------------------------------------------------------------
"""

from dataclasses import dataclass, field
from datetime import datetime

from app.models.pipeline.step_result import StepResult


@dataclass(slots=True)
class PipelineResult:
    """
    Resultado consolidado da execução da Pipeline.
    """

    success: bool = True

    started_at: datetime | None = None

    finished_at: datetime | None = None

    elapsed_seconds: float = 0.0

    failed_step: str | None = None

    message: str = ""

    steps: list[StepResult] = field(
        default_factory=list,
    )