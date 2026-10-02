"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_step.py
Descrição : Contrato base para todas as etapas da Pipeline.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.pipeline.pipeline_context import PipelineContext
from app.models.pipeline.step_result import StepResult


class PipelineStep(ABC):
    """
    Contrato base para todas as etapas da Pipeline.
    """

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Nome amigável da Step.
        """
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        context: PipelineContext,
    ) -> StepResult:
        """
        Executa uma etapa da Pipeline.
        """
        raise NotImplementedError

    def should_execute(
        self,
        context: PipelineContext,
    ) -> bool:
        """
        Indica se esta etapa deve ser executada.

        Quando retorna False, o StepExecutor não chama execute()
        e marca a etapa como SKIPPED. O padrão é sempre executar;
        etapas que suportam pular (por exemplo, quando o código-fonte
        não mudou desde o último build) sobrescrevem este método.
        """
        return True