"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : step_status.py
Descrição : Status da execução de uma etapa da Pipeline.
--------------------------------------------------------------------
"""

from enum import Enum


class StepStatus(str, Enum):
    """
    Representa o estado da execução de uma etapa da Pipeline.
    """

    SUCCESS = "success"

    FAILED = "failed"

    SKIPPED = "skipped"

    CANCELLED = "cancelled"