"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_session_info.py
Descrição : Representa as informações persistidas de uma sessão da
            Pipeline.
--------------------------------------------------------------------
"""

from datetime import datetime

from pydantic import BaseModel


class PipelineSessionInfo(
    BaseModel,
):
    """
    Informações persistidas de uma sessão.
    """

    session_id: str

    pipeline_name: str

    success: bool

    message: str

    started_at: datetime | None

    finished_at: datetime | None

    elapsed_seconds: float

    failed_step: str