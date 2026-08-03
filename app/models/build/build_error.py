"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_error.py
Descrição : Representa um erro encontrado durante uma Build.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass
class BuildError:
    """
    Representa um erro de compilação.
    """

    project: str = ""

    file: str = ""

    line: int = 0

    column: int = 0

    code: str = ""

    message: str = ""