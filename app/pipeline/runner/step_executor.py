"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : step_executor.py
Descrição : Responsável por executar uma Step da Pipeline.
--------------------------------------------------------------------
"""

from app.models.pipeline.pipeline_context import PipelineContext
from app.models.pipeline.step_result import StepResult
from app.pipeline.abstractions.pipeline_step import PipelineStep


class StepExecutor:
    """
    Executa uma Step individual.
    """

    def execute(
        self,
        step: PipelineStep,
        context: PipelineContext,
    ) -> StepResult:

        return step.execute(
            context,
        )