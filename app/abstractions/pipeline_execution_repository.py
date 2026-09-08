"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_execution_repository.py
Descrição : Contrato responsável pelo armazenamento das execuções
             da Pipeline.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod
from typing import Any

from app.models.pipeline.pipeline_result import (
    PipelineResult,
)


class PipelineExecutionRepository(
    ABC,
):
    """
    Define o contrato responsável por armazenar
    execuções da Pipeline.
    """

    @abstractmethod
    def save(
        self,
        result: PipelineResult,
    ) -> None:
        """
        Salva uma execução da Pipeline.
        """
        raise NotImplementedError()

    def get_all(self) -> list[dict[str, Any]]:
        """
        Retorna todas as execuções persistidas.
        """
        raise NotImplementedError()

    def get_by_execution_id(
        self,
        execution_id: str,
    ) -> dict[str, Any] | None:
        """
        Retorna uma execução pelo identificador da execução.
        """
        raise NotImplementedError()
