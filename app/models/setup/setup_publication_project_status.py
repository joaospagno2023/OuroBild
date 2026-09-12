"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publication_project_status.py
Descrição : Status de publicação associado a um projeto.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class SetupPublicationProjectStatus(BaseModel):
    """Representa o estado da publicação para um projeto."""

    project_id: str
    execution_id: str
    status: str
    message: str
