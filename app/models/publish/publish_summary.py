"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_summary.py
Descrição : Resumo da execução do Publish.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PublishSummary:
    """
    Resumo da execução do Publish.
    """

    #
    # Resultado
    #

    published: bool = False

    #
    # Configuração utilizada
    #

    configuration: str = ""

    framework: str = ""

    runtime: str = ""

    output_directory: str = ""

    publish_profile: str = ""

    #
    # Opções do Publish
    #

    self_contained: bool = False

    single_file: bool = False

    ready_to_run: bool = False

    trimmed: bool = False

    #
    # Estatísticas
    #

    total_errors: int = 0

    total_warnings: int = 0