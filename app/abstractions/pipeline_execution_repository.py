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