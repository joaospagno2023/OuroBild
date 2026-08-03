"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_warning.py
Descrição : Representa um aviso ocorrido durante o Publish.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PublishWarning:
    """
    Representa um aviso do Publish.
    """

    code: str = ""

    message: str = ""