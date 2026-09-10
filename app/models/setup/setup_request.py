"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_request.py
Descrição : Representa uma solicitação de geração de Setup.
--------------------------------------------------------------------
"""

from pydantic import BaseModel

from app.models.setup.setup_publication_mode import (
    SetupPublicationMode,
)


class SetupRequest(BaseModel):
    """
    Representa uma solicitação de geração de Setup.
    """

    #
    # Projeto
    #

    project_id: str

    environment_id: str

    #
    # Versionamento
    #

    version: str | None = None

    revision: int | None = None

    #
    # Build
    #

    run_build: bool = True

    #
    # Configuração do Setup
    #

    configuration: str = "Release"

    #
    # Publicação
    #

    publication_mode: SetupPublicationMode = (
        SetupPublicationMode.LOCAL
    )