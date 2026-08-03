"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_configuration.py
Descrição : Configuração das etapas da Pipeline.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class PipelineConfiguration(BaseModel):
    """
    Define quais etapas da Pipeline serão executadas.
    """

    restore: bool = True

    build: bool = True

    test: bool = False

    publish: bool = True

    installer: bool = False

    deploy: bool = False