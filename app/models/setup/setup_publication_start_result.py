"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publication_start_result.py
Descrição : Resposta inicial da publicação assíncrona de Setups.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class SetupPublicationStartResult(BaseModel):
    """Representa a resposta imediata ao iniciar uma publicação."""

    batch_id: str
    success: bool
    status: str
    message: str
    execution_ids: list[str]
    project_ids: list[str]
    source_path: str | None = None
