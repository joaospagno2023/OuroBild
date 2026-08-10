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
from pathlib import Path
from uuid import uuid4

from app.models.build.build_execution import (
    BuildExecution,
)
from app.models.pipeline.step_result import (
    StepResult,
)
from app.models.publish.publish_execution import (
    PublishExecution,
)


@dataclass(
    slots=True,
)
class PipelineResult:
    """
    Representa o resultado da execução de uma Pipeline.
    """

    #
    # Identificação
    #

    session_id: str = field(
        default_factory=lambda: uuid4().hex.upper()[:8],
    )

    #
    # Resultado geral
    #

    success: bool = True

    message: str = ""

    #
    # Tempo de execução
    #

    started_at: datetime | None = None

    finished_at: datetime | None = None

    elapsed_seconds: float = 0.0

    #
    # Diagnóstico
    #

    failed_step: str = ""

    #
    # Artefatos produzidos
    #

    output_folder: Path | None = None

    artifacts: list[Path] = field(
        default_factory=list,
    )

    #
    # Etapas executadas
    #

    steps: list[StepResult] = field(
        default_factory=list,
    )

    #
    # Resultados especializados
    #

    build: BuildExecution | None = None

    publish: PublishExecution | None = None