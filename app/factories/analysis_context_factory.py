"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : analysis_context_factory.py
Descrição : Responsável por criar um AnalysisContext.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.analyzers.analysis_context import (
    AnalysisContext,
)
from app.models.analyzers.analyze_request import (
    AnalyzeRequest,
)


class AnalysisContextFactory:
    """
    Responsável por criar o contexto
    utilizado durante a análise.
    """

    def create(
        self,
        request: AnalyzeRequest,
        project_file: Path,
    ) -> AnalysisContext:
        """
        Cria um contexto para análise.

        Args:
            request:
                Requisição da análise.

            project_file:
                Caminho completo do arquivo .csproj.

        Returns:
            Contexto utilizado durante a análise.
        """

        return AnalysisContext(

            request=request,

            project_file=project_file,

        )