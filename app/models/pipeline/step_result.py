"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : step_result.py
Descrição : Resultado retornado por uma etapa da Pipeline.
--------------------------------------------------------------------
"""

from dataclasses import dataclass, field
from typing import Any

from app.models.pipeline.step_status import StepStatus


@dataclass(slots=True)
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
    # Resultado produzido por um OutputParser.
    #
    # Exemplo:
    #   - BuildExecution
    #   - TestExecution
    #   - InstallerExecution
    #

    analysis: Any | None = None