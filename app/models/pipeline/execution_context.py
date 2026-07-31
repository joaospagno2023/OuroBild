"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execution_context.py
Descrição : Contexto da execução de uma Step.
--------------------------------------------------------------------
"""

from dataclasses import dataclass

from app.models.pipeline.pipeline import Pipeline
from app.models.pipeline.pipeline_context import PipelineContext


@dataclass(slots=True)
class ExecutionContext:
    """
    Informações compartilhadas durante a execução.
    """

    pipeline: Pipeline

    pipeline_context: PipelineContext

    retry: int = 0