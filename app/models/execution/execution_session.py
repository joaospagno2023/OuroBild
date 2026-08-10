"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execution_log.py
Descrição : Modelo responsável por representar uma execução da
            Engine.
--------------------------------------------------------------------
"""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel
from pydantic import Field


class ExecutionSession(
    BaseModel,
):
    """
    Representa uma execução da Engine.
    """

    session_id: str = Field(
        default_factory=lambda: uuid4().hex.upper()[:8],
    )

    category: str

    started_at: datetime

    finished_at: datetime

    duration: float

    success: bool

    executable: str

    working_directory: str

    command_line: str

    exit_code: int

    output_file: str = "output.log"

    metadata_file: str = "session.json"

    execution_folder: Path | None = None