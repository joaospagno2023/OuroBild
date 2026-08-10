"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_persistence_service.py
Descrição : Contrato responsável pela persistência da execução de
             uma Pipeline.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.pipeline.pipeline_result import (
    PipelineResult,
)


class PipelinePersistenceService(
    ABC,
):
    """
    Define o contrato responsável por persistir uma execução
    da Pipeline.
    """

    @abstractmethod
    def save(
        self,
        result: PipelineResult,
    ) -> None:
        """
        Persiste o resultado de uma Pipeline.
        """
        raise NotImplementedError()