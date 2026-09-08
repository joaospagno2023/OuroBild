"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_pipeline_execution_log_repository.py
Descrição : Repositório SQL Server responsável pelo armazenamento
             e consulta dos logs das execuções da Pipeline.
--------------------------------------------------------------------
"""

from sqlalchemy import select

from app.abstractions.pipeline_execution_log_repository import (
    PipelineExecutionLogRepository,
)
from app.database.connection import DatabaseConnection
from app.database.models.pipeline_execution_log_model import (
    PipelineExecutionLogModel,
)
from app.models.logging.pipeline_execution_log import (
    PipelineExecutionLog,
)


class SqlPipelineExecutionLogRepository(
    PipelineExecutionLogRepository
):
    """
    Implementação SQL Server do repositório de logs das
    execuções da Pipeline.
    """

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        """
        Inicializa o repositório.

        Args:
            database_connection:
                Conexão responsável pelo acesso ao SQL Server.
        """
        if database_connection is None:
            raise ValueError(
                "database_connection é obrigatório."
            )

        self.__database_connection = database_connection

    def save(
        self,
        log: PipelineExecutionLog,
    ) -> None:
        """
        Persiste um log de execução no SQL Server.

        Args:
            log:
                Log que será persistido.
        """
        if log is None:
            raise ValueError(
                "log é obrigatório."
            )

        model = PipelineExecutionLogModel(
            execution_id=log.execution_id,
            timestamp=log.timestamp,
            level=log.level,
            source=log.source,
            message=log.message,
            details=log.details,
        )

        with self.__database_connection.create_session() as session:
            session.add(model)
            session.commit()

    def get_by_execution_id(
        self,
        execution_id: str,
    ) -> list[PipelineExecutionLog]:
        """
        Retorna todos os logs de uma execução.

        Args:
            execution_id:
                Identificador da execução.

        Returns:
            Lista de logs ordenados por data/hora e Id.
        """
        if not execution_id:
            raise ValueError(
                "execution_id é obrigatório."
            )

        statement = (
            select(PipelineExecutionLogModel)
            .where(
                PipelineExecutionLogModel.execution_id
                == execution_id
            )
            .order_by(
                PipelineExecutionLogModel.timestamp,
                PipelineExecutionLogModel.id,
            )
        )

        with self.__database_connection.create_session() as session:
            models = session.scalars(statement).all()

        return [
            self.__to_domain(model)
            for model in models
        ]

    @staticmethod
    def __to_domain(
        model: PipelineExecutionLogModel,
    ) -> PipelineExecutionLog:
        """
        Converte o modelo SQLAlchemy para o modelo de domínio.

        Args:
            model:
                Modelo persistido no banco.

        Returns:
            Modelo de domínio PipelineExecutionLog.
        """
        return PipelineExecutionLog(
            execution_id=model.execution_id,
            timestamp=model.timestamp,
            level=model.level,
            source=model.source,
            message=model.message,
            details=model.details,
        )