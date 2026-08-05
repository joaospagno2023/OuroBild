"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_not_found_exception.py
Descrição : Projeto não encontrado.
--------------------------------------------------------------------
"""

from app.exceptions.ourobuild_exception import (
    OuroBuildException,
)

from app.models.api.api_error_code import (
    ErrorCode,
)


class ProjectNotFoundException(
    OuroBuildException,
):
    """
    Projeto solicitado não foi encontrado.
    """

    def __init__(
        self,
        project_id: str,
    ) -> None:

        super().__init__(
            code=ErrorCode.PROJECT_NOT_FOUND,
            message=(
                f"Projeto '{project_id}' não foi encontrado."
            ),
            status_code=404,
        )