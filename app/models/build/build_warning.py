"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_warning.py
Descrição : Representa um warning encontrado durante uma Build.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass
class BuildWarning:
    """
    Representa um warning de compilação.
    """

    project: str = ""

    file: str = ""

    line: int = 0

    column: int = 0

    code: str = ""

    message: str = ""