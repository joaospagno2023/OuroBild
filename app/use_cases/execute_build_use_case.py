"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execute_build_use_case.py
Descrição : Responsável por iniciar uma Build.
--------------------------------------------------------------------
"""

from app.models.build.build_request import BuildRequest


class ExecuteBuildUseCase:
    """
    Responsável por iniciar uma Build.
    """

    def execute(
        self,
        request: BuildRequest,
    ) -> dict:
        """
        Inicia uma Build.
        """

        return {
            "success": True,
            "message": "Nova Build Engine iniciada.",
            "request": request.model_dump(),
        }