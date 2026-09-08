"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_execution_log.py
Descrição :
    Modelo responsável por representar um log persistido de uma
    execução da Pipeline.
--------------------------------------------------------------------
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PipelineExecutionLog:
    """
    Representa um registro de log vinculado a uma execução.

    O ExecutionId identifica a execução da Pipeline à qual o log
    pertence.
    """

    execution_id: str
    timestamp: datetime
    level: str
    source: str | None
    message: str
    details: str | None = None