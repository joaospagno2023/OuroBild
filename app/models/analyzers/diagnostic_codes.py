"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : diagnostic_code.py
Descrição : Catálogo oficial de códigos de diagnóstico.
--------------------------------------------------------------------
"""

from enum import StrEnum


class DiagnosticCode(
    StrEnum,
):
    """
    Catálogo oficial de códigos de diagnóstico
    utilizados pelo OuroBuild.
    """

    # ==========================================================
    # Projeto (OB1xxx)
    # ==========================================================

    PROJECT_ASSEMBLY_NAME_MISSING = (
        "OB1001"
    )

    PROJECT_ROOT_NAMESPACE_MISSING = (
        "OB1002"
    )

    PROJECT_GUID_MISSING = (
        "OB1003"
    )

    # ==========================================================
    # Framework (OB2xxx)
    # ==========================================================

    # Reservado

    # ==========================================================
    # Build (OB3xxx)
    # ==========================================================

    # Reservado

    # ==========================================================
    # Dependências (OB4xxx)
    # ==========================================================

    # Reservado

    # ==========================================================
    # Publicação (OB5xxx)
    # ==========================================================

    # Reservado