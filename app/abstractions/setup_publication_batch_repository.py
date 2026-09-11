"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publication_batch_repository.py
Descrição : Contrato para persistência dos lotes de publicação.
--------------------------------------------------------------------
"""

from abc import ABC, abstractmethod

from app.models.setup.setup_publication_batch import (
    SetupPublicationBatch,
)


class SetupPublicationBatchRepository(ABC):
    """Define o contrato de persistência dos lotes."""

    @abstractmethod
    def save(
        self,
        batch: SetupPublicationBatch,
    ) -> None:
        """Insere um novo lote."""
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        batch: SetupPublicationBatch,
    ) -> None:
        """Atualiza um lote existente."""
        raise NotImplementedError

    @abstractmethod
    def get_by_batch_id(
        self,
        batch_id: str,
    ) -> SetupPublicationBatch | None:
        """Retorna um lote pelo identificador."""
        raise NotImplementedError
