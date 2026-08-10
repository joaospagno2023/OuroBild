"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execution_context.py
Descrição : Classe base para todos os Contextos de execução.
--------------------------------------------------------------------
"""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel
from pydantic import Field


class ExecutionContext(BaseModel):
    """
    Classe base para todos os Contextos utilizados
    durante a execução da Pipeline.
    """

    #
    # Estado
    #

    success: bool = True

    cancelled: bool = False

    #
    # Tempo
    #

    started_at: datetime | None = None

    finished_at: datetime | None = None

    elapsed_seconds: float = 0.0

    #
    # Diretórios
    #

    working_directory: Path | None = None

    output_directory: Path | None = None

    #
    # Mensagens
    #

    warnings: list[str] = Field(
        default_factory=list,
    )

    errors: list[str] = Field(
        default_factory=list,
    )

    messages: list[str] = Field(
        default_factory=list,
    )

    #
    # Dados auxiliares
    #

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )