"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publication_status_result.py
Descrição : Estado detalhado da publicação de Setups.
--------------------------------------------------------------------
"""

from pydantic import BaseModel, Field

from app.models.setup.setup_publication_project_status import (
    SetupPublicationProjectStatus,
)


class SetupPublicationStatusResult(BaseModel):
    """Representa o estado atual de uma publicação."""

    batch_id: str
    status: str
    success: bool | None = None
    message: str | None = None

    total: int = 0
    completed: int = 0
    failed: int = 0
    progress_percent: int = 0

    current_file: str | None = None
    current_file_index: int = 0
    total_files: int = 0

    projects: list[SetupPublicationProjectStatus] = Field(default_factory=list)
