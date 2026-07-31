"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_configuration.py
Descrição : Configuração da Pipeline.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PipelineConfiguration:
    """
    Configurações de execução da Pipeline.
    """

    continue_on_error: bool = False

    max_retries: int = 0

    timeout_seconds: int | None = None

    verbose: bool = False

    dry_run: bool = False