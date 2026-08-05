"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_to_analyze_mapper.py
Descrição : Converte um BuildRequest em AnalyzeRequest.
--------------------------------------------------------------------
"""

from app.models.analyzers.analyze_request import (
    AnalyzeRequest,
)

from app.models.build.build_request import (
    BuildRequest,
)


class BuildToAnalyzeMapper:
    """
    Responsável por converter um BuildRequest
    em um AnalyzeRequest.
    """

    def map(
        self,
        request: BuildRequest,
    ) -> AnalyzeRequest:
        """
        Converte uma requisição de Build em
        uma requisição de Analysis.
        """

        return AnalyzeRequest(

            project=request.project_id,

            environment=request.environment_id,

        )