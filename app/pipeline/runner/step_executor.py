"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : step_executor.py
Descrição : Responsável por executar uma etapa da Pipeline.
--------------------------------------------------------------------
"""

import traceback

from app.models.pipeline.pipeline import Pipeline
from app.models.pipeline.pipeline_context import PipelineContext
from app.models.pipeline.step_result import StepResult
from app.models.pipeline.step_status import StepStatus
from app.pipeline.abstractions.pipeline_step import PipelineStep


class StepExecutor:
    """
    Responsável por executar uma Step da Pipeline.
    """

    def execute(
        self,
        pipeline: Pipeline,
        step: PipelineStep,
        context: PipelineContext,
    ) -> StepResult:
        """
        Executa uma Step e retorna seu resultado.
        """

        try:

            

            step_result = step.execute(
                context,
            )

            

            if not step_result.name:
                step_result.name = step.name

            return step_result

        except Exception:

            
            traceback.print_exc()

            # Durante a depuração queremos ver a exceção real.
            raise