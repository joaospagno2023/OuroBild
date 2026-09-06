"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_execution_service.py
Descrição : Gerencia a execução assíncrona das Pipelines.
--------------------------------------------------------------------
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Lock
from typing import Callable
from uuid import uuid4

from app.models.execution.pipeline_execution_response import (
    PipelineExecutionResponse,
)
from app.models.execution.pipeline_execution_state import (
    PipelineExecutionPhase,
    PipelineExecutionState,
    PipelineExecutionStatus,
)
from app.use_cases.execute_pipeline_use_case import (
    ExecutePipelineUseCase,
)


PipelineProgressCallback = Callable[
    [
        str,
        int,
        int,
        int,
        PipelineExecutionPhase,
    ],
    None,
]


class PipelineExecutionService:
    """
    Gerencia execuções assíncronas da Pipeline.
    """

    def __init__(
        self,
        max_workers: int = 1,
    ) -> None:
        self.__executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="ourobuild-pipeline",
        )

        self.__states: dict[
            str,
            PipelineExecutionState,
        ] = {}

        self.__lock = Lock()

    def start(
        self,
        execute_pipeline_use_case: ExecutePipelineUseCase,
        project_id: str,
        environment_id: str | None = None,
        version: str | None = None,
        revision: int | None = None,
    ) -> PipelineExecutionResponse:
        """
        Cria uma execução e inicia seu processamento
        em background.
        """

        execution_id = (
            uuid4()
            .hex
            .upper()
        )

        state = PipelineExecutionState(
            execution_id=execution_id,
            project_id=project_id,
            status=PipelineExecutionStatus.PENDING,
        )

        with self.__lock:
            self.__states[execution_id] = state

        self.__executor.submit(
            self.__execute,
            execution_id,
            execute_pipeline_use_case,
            project_id,
            environment_id,
            version,
            revision,
        )

        return self.__to_response(
            state,
        )

    def get(
        self,
        execution_id: str,
    ) -> PipelineExecutionResponse | None:
        """
        Retorna o estado atual da execução.
        """

        with self.__lock:
            state = self.__states.get(
                execution_id,
            )

            if state is None:
                return None

            state_copy = state.model_copy(
                deep=True,
            )

        return self.__to_response(
            state_copy,
        )

    def __execute(
        self,
        execution_id: str,
        execute_pipeline_use_case: ExecutePipelineUseCase,
        project_id: str,
        environment_id: str | None,
        version: str | None,
        revision: int | None,
    ) -> None:
        """
        Executa uma Pipeline em background.
        """

        started_at = datetime.now()

        self.__update_state(
            execution_id=execution_id,
            status=PipelineExecutionStatus.RUNNING,
            started_at=started_at,
        )

        callback = (
            self.__create_progress_callback(
                execution_id,
            )
        )

        try:
            result = (
                execute_pipeline_use_case.execute(
                    project_id=project_id,
                    environment_id=environment_id,
                    version=version,
                    revision=revision,
                    progress_callback=callback,
                )
            )

            finished_at = datetime.now()

            status = (
                PipelineExecutionStatus.COMPLETED
                if result.success
                else PipelineExecutionStatus.FAILED
            )

            self.__update_state(
                execution_id=execution_id,
                status=status,
                message=result.message,
                finished_at=finished_at,
                elapsed_seconds=result.elapsed_seconds,
                success=result.success,
                failed_step=result.failed_step,
            )

        except Exception as exc:
            finished_at = datetime.now()

            elapsed_seconds = (
                finished_at - started_at
            ).total_seconds()

            self.__update_state(
                execution_id=execution_id,
                status=PipelineExecutionStatus.FAILED,
                message=str(exc),
                finished_at=finished_at,
                elapsed_seconds=elapsed_seconds,
                success=False,
            )

    def __create_progress_callback(
        self,
        execution_id: str,
    ) -> PipelineProgressCallback:
        """
        Cria o callback responsável por atualizar
        o progresso da execução.
        """

        def callback(
            current_step: str,
            current_step_index: int,
            total_steps: int,
            progress_percent: int,
            phase: PipelineExecutionPhase,
        ) -> None:
            self.__update_state(
                execution_id=execution_id,
                phase=phase,
                current_step=current_step,
                current_step_index=current_step_index,
                total_steps=total_steps,
                progress_percent=progress_percent,
            )

        return callback

    def __update_state(
        self,
        execution_id: str,
        **changes: object,
    ) -> None:
        """
        Atualiza o estado da execução de forma thread-safe.
        """

        with self.__lock:
            state = self.__states.get(
                execution_id,
            )

            if state is None:
                return

            for name, value in changes.items():
                setattr(
                    state,
                    name,
                    value,
                )

    @staticmethod
    def __to_response(
        state: PipelineExecutionState,
    ) -> PipelineExecutionResponse:
        """
        Converte o estado interno em resposta da API.
        """

        return PipelineExecutionResponse(
            execution_id=state.execution_id,
            project_id=state.project_id,
            status=state.status,
            phase=state.phase,
            current_step=state.current_step,
            current_step_index=state.current_step_index,
            total_steps=state.total_steps,
            progress_percent=state.progress_percent,
            message=state.message,
            started_at=state.started_at,
            finished_at=state.finished_at,
            elapsed_seconds=state.elapsed_seconds,
            success=state.success,
            failed_step=state.failed_step,
        )


_pipeline_execution_service = (
    PipelineExecutionService()
)


def get_pipeline_execution_service() -> (
    PipelineExecutionService
):
    """
    Retorna a instância compartilhada do serviço.
    """

    return _pipeline_execution_service