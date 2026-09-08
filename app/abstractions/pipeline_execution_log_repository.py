"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_execution_log_repository.py
Descrição : Contrato responsável pelo armazenamento dos logs
             das execuções da Pipeline.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.logging.pipeline_execution_log import (
    PipelineExecutionLog,
)


class PipelineExecutionLogRepository(
    ABC,
):
    """
    Define o contrato responsável por armazenar os logs
    das execuções da Pipeline.
    """

    @abstractmethod
    def save(
        self,
        log: PipelineExecutionLog,
    ) -> None:
        """
        Salva um log de execução da Pipeline.
        """

        raise NotImplementedError()

    @abstractmethod
    def get_by_execution_id(
        self,
        execution_id: str,
    ) -> list[PipelineExecutionLog]:
        """
        Retorna os logs de uma execução.
        """

        raise NotImplementedError()