"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publication_status_result.py
Descrição : Resultado do acompanhamento de um lote de publicação.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class SetupPublicationProjectStatus(BaseModel):
    """Status individual de um Setup participante do lote."""

    project_id: str
    execution_id: str
    status: str
    message: str


class SetupPublicationStatusResult(BaseModel):
    """Status consolidado de um lote de publicação."""

    batch_id: str
    status: str
    success: bool | None
    message: str | None
    total: int
    completed: int
    failed: int
    progress_percent: int
    projects: list[SetupPublicationProjectStatus]
