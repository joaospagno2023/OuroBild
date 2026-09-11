"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_setup_publication_batch_repository.py
Descrição : Repositório SQL Server dos lotes de publicação.
--------------------------------------------------------------------
"""

from pathlib import Path

from sqlalchemy import select

from app.abstractions.setup_publication_batch_repository import (
    SetupPublicationBatchRepository,
)
from app.database.connection import DatabaseConnection
from app.database.models.setup_publication_batch_model import (
    SetupPublicationBatchModel,
)
from app.models.setup.setup_publication_batch import (
    SetupPublicationBatch,
)


class SqlSetupPublicationBatchRepository(
    SetupPublicationBatchRepository,
):
    """Implementação SQL Server do repositório de lotes."""

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        if database_connection is None:
            raise ValueError(
                "A conexão com o banco de dados é obrigatória."
            )

        self.__database_connection = database_connection

    def save(
        self,
        batch: SetupPublicationBatch,
    ) -> None:
        if batch is None:
            raise ValueError("batch é obrigatório.")

        model = SetupPublicationBatchModel(
            batch_id=batch.batch_id,
            version=batch.version,
            revision=batch.revision,
            source_path=str(batch.source_path),
            destination_path=(
                str(batch.destination_path)
                if batch.destination_path is not None
                else None
            ),
            status=batch.status,
            started_at=batch.started_at,
            finished_at=batch.finished_at,
            elapsed_seconds=batch.elapsed_seconds,
            total_setups=batch.total_setups,
            completed_setups=batch.completed_setups,
            failed_setups=batch.failed_setups,
            message=batch.message,
        )

        with self.__database_connection.create_session() as session:
            session.add(model)
            session.commit()

    def update(
        self,
        batch: SetupPublicationBatch,
    ) -> None:
        if batch is None:
            raise ValueError("batch é obrigatório.")

        with self.__database_connection.create_session() as session:
            model = session.scalar(
                select(SetupPublicationBatchModel).where(
                    SetupPublicationBatchModel.batch_id
                    == batch.batch_id,
                )
            )

            if model is None:
                raise ValueError(
                    f"Batch não encontrado: {batch.batch_id}"
                )

            model.version = batch.version
            model.revision = batch.revision
            model.source_path = str(batch.source_path)
            model.destination_path = (
                str(batch.destination_path)
                if batch.destination_path is not None
                else None
            )
            model.status = batch.status
            model.started_at = batch.started_at
            model.finished_at = batch.finished_at
            model.elapsed_seconds = batch.elapsed_seconds
            model.total_setups = batch.total_setups
            model.completed_setups = batch.completed_setups
            model.failed_setups = batch.failed_setups
            model.message = batch.message

            session.commit()

    def get_by_batch_id(
        self,
        batch_id: str,
    ) -> SetupPublicationBatch | None:
        if not batch_id:
            raise ValueError("batch_id é obrigatório.")

        with self.__database_connection.create_session() as session:
            model = session.scalar(
                select(SetupPublicationBatchModel).where(
                    SetupPublicationBatchModel.batch_id
                    == batch_id,
                )
            )

        if model is None:
            return None

        return SetupPublicationBatch(
            batch_id=model.batch_id,
            version=model.version,
            revision=model.revision,
            source_path=Path(model.source_path),
            destination_path=(
                Path(model.destination_path)
                if model.destination_path
                else None
            ),
            status=model.status,
            started_at=model.started_at,
            finished_at=model.finished_at,
            elapsed_seconds=(
                float(model.elapsed_seconds)
                if model.elapsed_seconds is not None
                else None
            ),
            total_setups=model.total_setups,
            completed_setups=model.completed_setups,
            failed_setups=model.failed_setups,
            message=model.message,
        )
