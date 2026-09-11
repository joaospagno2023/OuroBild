"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publication_log_repository.py
Descrição : Contrato para persistência dos logs de publicação.
--------------------------------------------------------------------
"""

from abc import ABC, abstractmethod

from app.models.setup.setup_publication_log import SetupPublicationLog


class SetupPublicationLogRepository(ABC):
    """Define o contrato de persistência dos logs de publicação."""

    @abstractmethod
    def save(
        self,
        log: SetupPublicationLog,
    ) -> None:
        """Persiste um evento de publicação."""
        raise NotImplementedError

    @abstractmethod
    def get_by_batch_id(
        self,
        batch_id: str,
    ) -> list[SetupPublicationLog]:
        """Retorna os eventos de um lote."""
        raise NotImplementedError
