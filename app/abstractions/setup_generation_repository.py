"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_generation_repository.py
Descrição : Contrato responsável pelo armazenamento das gerações
             de Setup.
--------------------------------------------------------------------
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class SetupGenerationRepository(ABC):
    """
    Define o contrato responsável por armazenar e consultar
    gerações de Setup.
    """

    @abstractmethod
    def create_generation(
        self,
        generation_id: str,
        environment_id: str,
        version: str | None,
        revision: int | None,
        started_at: datetime,
        execution_id: str | None = None,
        validity_minutes: int = 5,
        created_by: str | None = None,
    ) -> None:
        """
        Cria uma nova geração de Setup.
        """
        raise NotImplementedError()

    @abstractmethod
    def finish_generation(
        self,
        generation_id: str,
        status: str,
        finished_at: datetime | None,
        last_file_path: str | None = None,
        last_file_generated_at: datetime | None = None,
    ) -> None:
        """
        Finaliza uma geração de Setup.
        """
        raise NotImplementedError()

    @abstractmethod
    def register_file(
        self,
        generation_id: str,
        project_id: str,
        file_path: str,
        generated_at: datetime,
        success: bool,
    ) -> None:
        """
        Registra um arquivo produzido pela geração.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_by_generation_id(
        self,
        generation_id: str,
    ) -> dict[str, Any] | None:
        """
        Retorna uma geração pelo GenerationId.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_files(
        self,
        generation_id: str,
    ) -> list[dict[str, Any]]:
        """
        Retorna os arquivos registrados em uma geração.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_latest(
        self,
        environment_id: str,
        version: str | None,
        revision: int | None,
    ) -> dict[str, Any] | None:
        """
        Retorna a geração mais recente para ambiente,
        versão e revisão.
        """
        raise NotImplementedError()