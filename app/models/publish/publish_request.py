"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_request.py
Descrição : Representa uma solicitação de Publish.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class PublishRequest(BaseModel):
    """
    Representa uma solicitação de execução de Publish.
    """

    project_id: str

    environment_id: str

    configuration: str = "Release"

    output_directory: str | None = None

    runtime: str | None = None

    framework: str | None = None

    self_contained: bool = False

    publish_profile: str | None = None

    single_file: bool = False

    ready_to_run: bool = False

    trimmed: bool = False