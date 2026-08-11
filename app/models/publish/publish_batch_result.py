"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_batch_result.py
Descrição : Resultado da execução de Publish para múltiplos projetos.
--------------------------------------------------------------------
"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime

from app.models.pipeline.pipeline_result import PipelineResult


@dataclass(slots=True)
class PublishBatchResult:
    """
    Representa o resultado de uma execução de Publish
    envolvendo múltiplos projetos.
    """

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

    failed_project: str = ""

    #
    # Resultados individuais
    #

    projects: list[PipelineResult] = field(
        default_factory=list,
    )