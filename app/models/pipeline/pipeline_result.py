"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_result.py
Descrição : Resultado da execução de uma Pipeline.
--------------------------------------------------------------------
"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime

from app.models.build.build_execution import (
    BuildExecution,
)
from app.models.pipeline.step_result import StepResult
from app.models.publish.publish_execution import (
    PublishExecution,
)


@dataclass(slots=True)
class PipelineResult:
    """
    Representa o resultado da execução de uma Pipeline.
    """

    success: bool = True

    message: str = ""

    started_at: datetime | None = None

    finished_at: datetime | None = None

    elapsed_seconds: float = 0.0

    failed_step: str = ""

    steps: list[StepResult] = field(
        default_factory=list,
    )

    #
    # Resultados especializados.
    #

    build: BuildExecution | None = None

    publish: PublishExecution | None = None