"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : process_status.py
Descrição : Status possíveis da execução de um processo.
--------------------------------------------------------------------
"""

from enum import Enum


class ProcessStatus(str, Enum):
    """
    Representa o resultado da execução de um processo.
    """

    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"