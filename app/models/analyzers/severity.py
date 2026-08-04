"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : severity.py
Descrição : Define o nível de severidade de um diagnóstico.
--------------------------------------------------------------------
"""

from enum import StrEnum


class Severity(
    StrEnum,
):
    """
    Representa o nível de severidade
    de um diagnóstico.
    """

    INFO = "info"

    WARNING = "warning"

    ERROR = "error"