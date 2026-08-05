"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_decision.py
Descrição : Representa o plano de execução de um Build.
--------------------------------------------------------------------
"""

from dataclasses import dataclass, field


@dataclass
class BuildDecision:
    """
    Representa todas as decisões tomadas
    antes da execução do Build.
    """

    #
    # Ferramenta de Build
    #

    builder: str = "msbuild"

    #
    # Etapas da execução
    #

    restore_packages: bool = False

    clean_before_build: bool = False

    publish_after_build: bool = False

    #
    # Características do projeto
    #

    sdk_style: bool = False

    executable: bool = False

    web_project: bool = False

    windows_service: bool = False

    sign_assembly: bool = False

    #
    # Plano de execução
    #

    execution_plan: list[str] = field(
        default_factory=list,
    )