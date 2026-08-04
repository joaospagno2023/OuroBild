"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : analysis_status.py
Descrição : Define o resultado geral de uma análise.
--------------------------------------------------------------------
"""

from enum import StrEnum


class AnalysisStatus(
    StrEnum,
):
    """
    Representa o resultado geral
    de uma análise.
    """

    SUCCESS = "success"

    WARNING = "warning"

    FAILED = "failed"