"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : process_result.py
Descrição : Resultado da execução de um processo.
--------------------------------------------------------------------
"""

from datetime import datetime

from pydantic import BaseModel

from app.models.process.process_status import (
    ProcessStatus,
)


class ProcessResult(
    BaseModel,
):
    """
    Resultado da execução de um processo.
    """

    status: ProcessStatus

    exit_code: int

    stdout: str

    stderr: str

    duration: float

    started_at: datetime

    finished_at: datetime

    executable: str

    working_directory: str

    command_line: str