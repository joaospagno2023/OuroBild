"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_environment_type.py
Descrição : Tipos de ambientes suportados pelo OuroBuild.
--------------------------------------------------------------------
"""

from enum import Enum


class BuildEnvironmentType(str, Enum):
    """
    Tipos de ambiente de Build.
    """

    VERSIONED = "versioned"

    PRODUCTION = "production"