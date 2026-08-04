"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : error_code.py
Descrição : Catálogo oficial de códigos de erro.
--------------------------------------------------------------------
"""

from enum import StrEnum


class ErrorCode(
    StrEnum,
):
    """
    Códigos oficiais de erro da aplicação.
    """

    #
    # Arquivos
    #

    PROJECT_FILE_NOT_FOUND = "OB0001"

    INVALID_PROJECT_FILE = "OB0002"

    #
    # Workspace
    #

    PROJECT_NOT_FOUND = "OB0003"

    ENVIRONMENT_NOT_FOUND = "OB0004"

    #
    # Build
    #

    BUILD_FAILED = "OB0005"

    #
    # Publish
    #

    PUBLISH_FAILED = "OB0006"

    #
    # Infraestrutura
    #

    INTERNAL_ERROR = "OB9999"