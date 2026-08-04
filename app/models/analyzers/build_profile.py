"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_profile.py
Descrição : Representa o perfil de compilação de um projeto.
--------------------------------------------------------------------
"""

from dataclasses import dataclass

from app.models.build.compilation_engine import (
    CompilationEngine,
)


@dataclass(
    frozen=True,
    slots=True,
)
class BuildProfile:
    """
    Representa o perfil de compilação
    identificado durante a análise.
    """

    compilation_engine: CompilationEngine

    output_type: str = ""

    sign_assembly: bool = False

    assembly_originator_key_file: str = ""