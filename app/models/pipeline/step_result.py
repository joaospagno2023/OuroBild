"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : step_result.py
Descrição : Resultado retornado por uma etapa da Pipeline.
--------------------------------------------------------------------
"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Any

from app.models.pipeline.step_status import (
    StepStatus,
)
from app.models.process.process_result import (
    ProcessResult,
)


@dataclass(
    slots=True,
)
class StepResult:
    """
    Representa o resultado da execução de uma etapa da Pipeline.
    """

    #
    # Identificação
    #

    name: str = ""

    #
    # Resultado
    #

    status: StepStatus = StepStatus.SUCCESS

    message: str = ""

    started_at: datetime | None = None

    finished_at: datetime | None = None

    elapsed_seconds: float = 0.0

    #
    # Diagnóstico
    #

    warnings: list[str] = field(
        default_factory=list,
    )

    errors: list[str] = field(
        default_factory=list,
    )

    #
    # Processo executado
    #

    process: ProcessResult | None = None

    #
    # Arquivos produzidos
    #

    output_log: Path | None = None

    #
    # Resultado produzido pelo OutputParser
    #

    analysis: Any | None = None