"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_pipeline_execution_log_repository.py
Descrição : Testes do repositório SQL Server de logs das execuções.
--------------------------------------------------------------------
"""

from app.bootstrap import Bootstrap
from app.repositories.sql_pipeline_execution_log_repository import (
    SqlPipelineExecutionLogRepository,
)


def test_pipeline_execution_log_repository_read() -> None:
    """
    Valida a criação do repositório e a consulta de logs.

    A consulta utiliza um ExecutionId inexistente para garantir
    que nenhuma informação seja alterada no banco.
    """

    bootstrap = Bootstrap()

    repository = SqlPipelineExecutionLogRepository(
        database_connection=bootstrap.database_connection
    )

    execution_id = "TEST_EXECUTION_ID_NOT_EXISTS"

    logs = repository.get_by_execution_id(
        execution_id
    )

    assert logs == []