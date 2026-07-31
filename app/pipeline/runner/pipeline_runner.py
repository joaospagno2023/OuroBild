"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_runner.py
Descrição : Responsável por executar as etapas da Pipeline.
--------------------------------------------------------------------
"""

from datetime import datetime

from app.models.pipeline.pipeline import Pipeline
from app.models.pipeline.pipeline_context import PipelineContext
from app.models.pipeline.pipeline_result import PipelineResult
from app.models.pipeline.step_result import StepResult
from app.models.pipeline.step_status import StepStatus


class PipelineRunner:
    """
    Executa todas as etapas de uma Pipeline.
    """

    def execute(
        self,
        pipeline: Pipeline,
        context: PipelineContext,
    ) -> PipelineResult:
        """
        Executa todas as etapas da Pipeline.
        """

        result = PipelineResult()

        result.started_at = datetime.now()

        try:

            for step in pipeline.steps:

                try:

                    step_result = step.execute(
                        context,
                    )
                    result.steps.append(step_result)
                    
                except Exception as exception:

                    step_result = StepResult(
                        name=step.__class__.__name__,
                        status=StepStatus.FAILED,
                        message=str(exception),
                        errors=[
                            str(exception),
                        ],
                    )

                if not step_result.name:
                    step_result.name = step.__class__.__name__

                result.steps.append(
                    step_result,
                )

                if step_result.status == StepStatus.FAILED:

                    result.success = False
                    result.failed_step = step_result.name
                    result.message = step_result.message

                if not pipeline.configuration.continue_on_error:
                    break

        finally:

            result.finished_at = datetime.now()

            if result.started_at is not None:

                result.elapsed_seconds = (
                    result.finished_at - result.started_at
                ).total_seconds()

        return result