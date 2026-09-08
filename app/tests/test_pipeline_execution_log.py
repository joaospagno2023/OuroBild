"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_pipeline_execution_log.py
Descrição : Teste manual da persistência de logs de execução.
--------------------------------------------------------------------
"""

from datetime import datetime

from app.bootstrap import Bootstrap
from app.models.logging.pipeline_execution_log import (
    PipelineExecutionLog,
)


bootstrap = Bootstrap()

repository = bootstrap.pipeline_execution_log_repository
execution_repository = bootstrap.pipeline_execution_repository

executions = execution_repository.get_all()

if not executions:
    raise RuntimeError(
        "Nenhuma execução encontrada em PipelineExecutions."
    )

execution = executions[0]

execution_id = execution["execution_id"]

print(
    f"ExecutionId utilizado no teste: {execution_id}"
)

log = PipelineExecutionLog(
    execution_id=execution_id,
    timestamp=datetime.now(),
    level="INFO",
    source="Teste",
    message="Teste de persistência do PipelineExecutionLogs",
    details=None,
)

print("Gravando log...")

repository.save(log)

print("Log gravado com sucesso.")

logs = repository.get_by_execution_id(
    execution_id,
)

print(
    f"Quantidade de logs encontrados: {len(logs)}"
)

for item in logs:
    print(
        f"{item.timestamp} | "
        f"{item.level} | "
        f"{item.source} | "
        f"{item.message}"
    )