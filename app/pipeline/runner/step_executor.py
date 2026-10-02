"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : step_executor.py
Descrição : Responsável por executar uma etapa da Pipeline.
--------------------------------------------------------------------
"""

import traceback
from datetime import datetime

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

            if not step.should_execute(context):

                now = datetime.now()

                return StepResult(
                    name=step.name,
                    status=StepStatus.SKIPPED,
                    message=(
                        "Etapa pulada: sem alterações no "
                        "código-fonte desde o último build "
                        "bem-sucedido."
                    ),
                    started_at=now,
                    finished_at=now,
                    elapsed_seconds=0.0,
                )

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