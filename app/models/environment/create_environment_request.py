"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : create_environment_request.py
Descrição : Dados necessários para criação de um ambiente.
--------------------------------------------------------------------
"""

from pydantic import BaseModel

from app.models.environment.build_environment_type import (
    BuildEnvironmentType,
)


class CreateEnvironmentRequest(
    BaseModel,
):
    """
    Representa os dados necessários para criar um ambiente.
    """

    id: str

    name: str

    resolver: BuildEnvironmentType

    root_path: str