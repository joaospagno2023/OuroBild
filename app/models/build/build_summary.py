"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_summary.py
Descrição : Resumo da execução da Build.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass
class BuildSummary:
    """
    Resumo da Build.
    """

    total_errors: int = 0

    total_warnings: int = 0

    build_succeeded: bool = False