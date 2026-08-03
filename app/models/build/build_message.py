"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_message.py
Descrição : Modelo base para mensagens de Build.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass
class BuildMessage:
    """
    Representa uma mensagem produzida durante a Build.
    """

    project: str = ""

    file: str = ""

    line: int = 0

    column: int = 0

    code: str = ""

    message: str = ""