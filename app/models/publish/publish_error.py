"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_error.py
Descrição : Representa um erro ocorrido durante o Publish.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PublishError:
    """
    Representa um erro do Publish.
    """

    code: str = ""

    message: str = ""