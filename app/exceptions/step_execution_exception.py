"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : step_execution_exception.py
Descrição : Erro durante a execução de uma Step.
--------------------------------------------------------------------
"""

from app.exceptions.pipeline_exception import PipelineException


class StepExecutionException(PipelineException):
    """
    Erro ocorrido durante a execução de uma Step.
    """

    pass