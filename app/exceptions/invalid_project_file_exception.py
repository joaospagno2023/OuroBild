"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : invalid_project_file_exception.py
Descrição : Exceção lançada quando um .csproj é inválido.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.exceptions.ourobuild_exception import (
    OuroBuildException,
)

from app.models.api.api_error_code import (
    ErrorCode,
)


class InvalidProjectFileException(
    OuroBuildException,
):
    """
    Arquivo .csproj inválido.
    """

    def __init__(
        self,
        project_file: Path,
    ) -> None:

        super().__init__(

            code=ErrorCode.INVALID_PROJECT_FILE,

            message=(
                f"Arquivo inválido: "
                f"{project_file}"
            ),

            status_code=400,
        )

        self.project_file = project_file