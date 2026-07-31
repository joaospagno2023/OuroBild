"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : step_result.py
Descrição : Resultado retornado por uma etapa da Pipeline.
--------------------------------------------------------------------
"""

from dataclasses import dataclass, field

from app.models.pipeline.step_status import StepStatus


@dataclass(slots=True)
class StepResult:
    """
    Representa o resultado da execução de uma etapa da Pipeline.
    """

    name: str = ""

    status: StepStatus = StepStatus.SUCCESS

    message: str = ""

    elapsed_seconds: float = 0.0

    warnings: list[str] = field(
        default_factory=list,
    )

    errors: list[str] = field(
        default_factory=list,
    )