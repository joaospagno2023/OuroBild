"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_setup_publication_log_repository.py
Descrição : Repositório SQL Server dos logs de publicação.
--------------------------------------------------------------------
"""

from sqlalchemy import select

from app.abstractions.setup_publication_log_repository import (
    SetupPublicationLogRepository,
)
from app.database.connection import DatabaseConnection
from app.database.models.setup_publication_log_model import (
    SetupPublicationLogModel,
)
from app.models.setup.setup_publication_log import SetupPublicationLog


class SqlSetupPublicationLogRepository(
    SetupPublicationLogRepository,
):
    """Implementação SQL Server do repositório de logs."""

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
        log: SetupPublicationLog,
    ) -> None:
        if log is None:
            raise ValueError("log é obrigatório.")

        model = SetupPublicationLogModel(
            batch_id=log.batch_id,
            timestamp=log.timestamp,
            level=log.level,
            event_type=log.event_type,
            project_id=log.project_id,
            execution_id=log.execution_id,
            message=log.message,
            details=log.details,
        )

        with self.__database_connection.create_session() as session:
            session.add(model)
            session.commit()

    def get_by_batch_id(
        self,
        batch_id: str,
    ) -> list[SetupPublicationLog]:
        if not batch_id:
            raise ValueError("batch_id é obrigatório.")

        statement = (
            select(SetupPublicationLogModel)
            .where(
                SetupPublicationLogModel.batch_id == batch_id,
            )
            .order_by(
                SetupPublicationLogModel.timestamp,
                SetupPublicationLogModel.id,
            )
        )

        with self.__database_connection.create_session() as session:
            models = session.scalars(statement).all()

        return [
            SetupPublicationLog(
                batch_id=model.batch_id,
                timestamp=model.timestamp,
                level=model.level,
                event_type=model.event_type,
                project_id=model.project_id,
                execution_id=model.execution_id,
                message=model.message,
                details=model.details,
            )
            for model in models
        ]
