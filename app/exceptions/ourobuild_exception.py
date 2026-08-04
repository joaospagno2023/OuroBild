"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : ourobuild_exception.py
Descrição : Exceção base da aplicação.
--------------------------------------------------------------------
"""

from app.models.api.api_error_code import (
    ErrorCode,
)


class OuroBuildException(
    Exception,
):
    """
    Exceção base do OuroBuild.
    """

    def __init__(
        self,
        *,
        code: ErrorCode,
        message: str,
        status_code: int,
    ) -> None:

        super().__init__(message)

        self.code = code
        self.message = message
        self.status_code = status_code