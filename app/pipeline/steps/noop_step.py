"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : noop_step.py
Descrição : Etapa utilizada para validar o funcionamento da Pipeline.
--------------------------------------------------------------------
"""

from app.models.pipeline.step_result import StepResult
from app.pipeline.abstractions.pipeline_step import PipelineStep
from app.pipeline.context.pipeline_context import PipelineContext


class NoOpStep(PipelineStep):
    """
    Etapa que não executa nenhuma ação.
    Utilizada para validar a infraestrutura da Pipeline.
    """

    def execute(
        self,
        context: PipelineContext,
    ) -> StepResult:

        return StepResult(
            status=True,
            message="NoOp executado com sucesso.",
        )