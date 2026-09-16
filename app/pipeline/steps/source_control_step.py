"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : source_control_step.py
Descrição : Verifica alterações nos fontes e executa Get Last quando
             necessário, antes do Clean/Build.
--------------------------------------------------------------------
"""

from datetime import datetime

from app.abstractions.process_service import ProcessService
from app.models.pipeline.pipeline_context import PipelineContext
from app.models.pipeline.step_result import StepResult
from app.models.pipeline.step_status import StepStatus
from app.services.source_control_service import SourceControlService
from app.utils.pipeline_logger import PipelineLogger
from app.pipeline.abstractions.pipeline_step import PipelineStep


class SourceControlStep(PipelineStep):
    """Executa a política de Get Last baseada no hash dos fontes."""

    @property
    def name(self) -> str:
        return "Source Control"

    def __init__(
        self,
        process_service: ProcessService,
        source_control_service: SourceControlService,
    ) -> None:
        if process_service is None:
            raise ValueError("ProcessService não foi informado.")
        if source_control_service is None:
            raise ValueError("SourceControlService não foi informado.")
        self.__process_service = process_service
        self.__source_control_service = source_control_service

    def execute(self, context: PipelineContext) -> StepResult:
        started_at = datetime.now()

        build_context = context.variables["build_context"]
        project = build_context.project
        source_root = build_context.paths.source_root

        PipelineLogger.info(
            "SOURCE CONTROL STEP - INÍCIO - "
            f"Projeto: {project.id}"
        )

        get_last_executed, process, final_hash = (
            self.__source_control_service.synchronize(
                project_id=project.id,
                source_root=source_root,
            )
        )

        context.metadata["source_hash"] = final_hash
        context.metadata["get_last_executed"] = get_last_executed

        finished_at = datetime.now()

        if process is not None and process.status.value != "success":
            return StepResult(
                name=self.name,
                status=StepStatus.FAILED,
                message=(
                    "Falha durante o Get Last. "
                    f"ExitCode: {process.exit_code}. "
                    f"{process.stderr or process.stdout}".strip()
                ),
                started_at=started_at,
                finished_at=finished_at,
                elapsed_seconds=(finished_at - started_at).total_seconds(),
                errors=["Get Last falhou."],
                process=process,
            )

        message = (
            "Get Last executado com sucesso."
            if get_last_executed
            else "Nenhuma alteração detectada. Get Last ignorado."
        )

        PipelineLogger.info(
            f"SOURCE CONTROL STEP - {message}"
        )

        return StepResult(
            name=self.name,
            status=StepStatus.SUCCESS,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
            elapsed_seconds=(finished_at - started_at).total_seconds(),
            process=process,
        )
