"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_status.py
Descrição : Status possíveis de uma execução de build.
--------------------------------------------------------------------
"""

from enum import Enum


class BuildStatus(str, Enum):
    """
    Representa o resultado da execução de um build.
    """

    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"