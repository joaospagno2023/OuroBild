"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : diagnostic.py
Descrição : Representa um diagnóstico encontrado durante a análise.
--------------------------------------------------------------------
"""

from dataclasses import dataclass

from app.models.analyzers.severity import Severity


@dataclass(
    frozen=True,
    slots=True,
)
class Diagnostic:
    """
    Representa um diagnóstico identificado
    durante a análise de um projeto.
    """

    code: str

    severity: Severity

    message: str

    source: str