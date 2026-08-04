"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_file_not_found_exception.py
Descrição : Exceção lançada quando o arquivo do projeto não existe.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.exceptions.ourobuild_exception import (
    OuroBuildException,
)

from app.models.api.api_error_code import (
    ErrorCode,
)


class ProjectFileNotFoundException(
    OuroBuildException,
):
    """
    Arquivo .csproj não encontrado.
    """

    def __init__(
        self,
        project_file: Path,
    ) -> None:

        super().__init__(

            code=ErrorCode.PROJECT_FILE_NOT_FOUND,

            message=(
                f"Arquivo do projeto não encontrado: "
                f"{project_file}"
            ),

            status_code=404,
        )

        self.project_file = project_file