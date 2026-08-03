"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_runner.py
Descrição : Responsável por executar as etapas da Pipeline.
--------------------------------------------------------------------
"""

from datetime import datetime

from app.models.build.build_execution import BuildExecution
from app.models.pipeline.pipeline import Pipeline
from app.models.pipeline.pipeline_context import PipelineContext
from app.models.pipeline.pipeline_result import PipelineResult
from app.models.pipeline.step_status import StepStatus
from app.pipeline.runner.step_executor import StepExecutor


class PipelineRunner:
    """
    Executa todas as etapas de uma Pipeline.
    """

    def __init__(
        self,
    ) -> None:

        self._step_executor = StepExecutor()

    def execute(
        self,
        pipeline: Pipeline,
        context: PipelineContext,
    ) -> PipelineResult:
        """
        Executa todas as etapas da Pipeline.
        """

        result = PipelineResult(
            started_at=datetime.now(),
        )

        try:

            for step in pipeline.steps:

                step_result = self._step_executor.execute(
                    pipeline=pipeline,
                    step=step,
                    context=context,
                )

                result.steps.append(
                    step_result,
                )

                #
                # Promove a análise da Build para o
                # resultado consolidado da Pipeline.
                #

                if isinstance(
                    step_result.analysis,
                    BuildExecution,
                ):
                    result.build = (
                        step_result.analysis
                    )

                if step_result.status == StepStatus.FAILED:

                    result.success = False
                    result.failed_step = (
                        step_result.name
                    )
                    result.message = (
                        step_result.message
                    )

                    if (
                        not pipeline.configuration.continue_on_error
                    ):
                        break

        finally:

            finished_at = datetime.now()

            result.finished_at = finished_at

            if result.started_at is not None:

                result.elapsed_seconds = (
                    finished_at - result.started_at
                ).total_seconds()

        return result