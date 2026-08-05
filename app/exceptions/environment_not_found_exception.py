"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : environment_not_found_exception.py
Descrição : Ambiente não encontrado.
--------------------------------------------------------------------
"""

from app.exceptions.ourobuild_exception import (
    OuroBuildException,
)

from app.models.api.api_error_code import (
    ErrorCode,
)


class EnvironmentNotFoundException(
    OuroBuildException,
):
    """
    Ambiente solicitado não foi encontrado.
    """

    def __init__(
        self,
        environment_id: str,
    ) -> None:

        super().__init__(
            code=ErrorCode.ENVIRONMENT_NOT_FOUND,
            message=(
                f"Ambiente '{environment_id}' não foi encontrado."
            ),
            status_code=404,
        )