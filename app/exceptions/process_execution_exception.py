"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : process_execution_exception.py
Descrição : Erro na execução de um processo externo.
--------------------------------------------------------------------
"""

from app.exceptions.step_execution_exception import (
    StepExecutionException,
)


class ProcessExecutionException(
    StepExecutionException,
):
    """
    Erro durante a execução de um processo externo.
    """

    pass