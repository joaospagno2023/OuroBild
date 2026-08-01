"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_definition.py
Descrição : Define como um projeto deve ser compilado.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class BuildDefinition(BaseModel):
    """
    Define como um projeto deve ser compilado.
    """

    id: str

    name: str

    pipeline: str = "default"

    configuration: str = "Release"

    platform: str = "Any CPU"

    restore: bool = True

    build: bool = True

    publish: bool = True

    generate_installer: bool = True

    deploy: bool = False