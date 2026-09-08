"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_history_logs.py
Descrição : Logs associados a uma execução da Pipeline.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class PipelineHistoryLogs(BaseModel):
    """
    Representa os logs persistidos de uma execução.
    """

    execution_id: str
    content: str