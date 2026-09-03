"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_result.py
Descrição : Resultado da geração de Setup.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel, Field

from app.models.pipeline.step_result import StepResult


class SetupResult(BaseModel):
    """Resultado da geração de um Setup."""

    success: bool
    message: str
    project_id: str
    output_msi: Path | None = None
    duration_seconds: float = 0.0
    steps: list[StepResult] = Field(
        default_factory=list,
    )
