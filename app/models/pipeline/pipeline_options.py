"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_options.py
Descrição : Opções de execução da Pipeline.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PipelineOptions:
    """
    Configurações de execução da Pipeline.
    """

    continue_on_error: bool = False

    max_retries: int = 0

    timeout_seconds: int | None = None

    verbose: bool = False

    dry_run: bool = False