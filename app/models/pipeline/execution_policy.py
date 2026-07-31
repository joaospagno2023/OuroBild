"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execution_policy.py
Descrição : Configuração da política de execução da Pipeline.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ExecutionPolicy:
    """
    Define como a Pipeline deve ser executada.
    """

    continue_on_error: bool = False

    stop_on_first_failure: bool = True

    max_retries: int = 0

    timeout_seconds: int | None = None