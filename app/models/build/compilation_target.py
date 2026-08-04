"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : compilation_target.py
Descrição : Define o alvo da compilação.
--------------------------------------------------------------------
"""

from enum import Enum


class CompilationTarget(
    str,
    Enum,
):
    """
    Define qual arquivo será utilizado
    durante a compilação.
    """

    PROJECT = "project"

    SOLUTION = "solution"