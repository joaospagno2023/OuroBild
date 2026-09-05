"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : update_environment_request.py
Descrição : Dados necessários para atualização de um ambiente.
--------------------------------------------------------------------
"""

from pydantic import BaseModel

from app.models.environment.build_environment_type import (
    BuildEnvironmentType,
)


class UpdateEnvironmentRequest(
    BaseModel,
):
    """
    Representa os dados necessários para atualizar um ambiente.

    O identificador do ambiente não pode ser alterado.
    """

    name: str

    resolver: BuildEnvironmentType

    root_path: str