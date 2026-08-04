"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : api_error_response.py
Descrição : Modelo padrão de resposta de erro da API.
--------------------------------------------------------------------
"""

from pydantic import BaseModel

from app.models.api.api_error_code import (
    ErrorCode,
)


class ApiErrorResponse(
    BaseModel,
):
    """
    Resposta padrão de erro.
    """

    code: ErrorCode

    message: str