"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : analysis_context.py
Descrição : Contexto utilizado durante a análise.
--------------------------------------------------------------------
"""

from dataclasses import dataclass
from pathlib import Path

from app.models.analyzers.analyze_request import (
    AnalyzeRequest,
)


@dataclass(
    slots=True,
)
class AnalysisContext:
    """
    Contexto utilizado durante a execução
    da análise.
    """

    request: AnalyzeRequest

    project_file: Path