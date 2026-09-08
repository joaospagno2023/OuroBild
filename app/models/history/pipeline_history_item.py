"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_history_item.py
Descrição : Item resumido do histórico de execuções.
--------------------------------------------------------------------
"""

from datetime import datetime

from pydantic import BaseModel


class PipelineHistoryItem(BaseModel):
    """
    Representa uma execução no histórico.
    """

    execution_id: str
    project_id: str
    project_name: str
    session_id: str
    version: str | None
    success: bool
    status: str
    message: str
    started_at: datetime | None
    finished_at: datetime | None
    elapsed_seconds: float
    failed_step: str | None
    steps_count: int
