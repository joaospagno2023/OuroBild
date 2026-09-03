"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execute_pipeline_use_case.py
Descrição : Responsável por executar uma Pipeline de Build.
--------------------------------------------------------------------
"""

from app.abstractions.pipeline_factory import PipelineFactory
from app.abstractions.project_repository import ProjectRepository
from app.exceptions.project_not_found_exception import (
    ProjectNotFoundException,
)
from app.models.pipeline.pipeline_context import PipelineContext
from app.models.pipeline.pipeline_result import PipelineResult
from app.models.setup.setup_request import SetupRequest
from app.pipeline.runner.pipeline_runner import PipelineRunner
from app.use_cases.execute_setup_use_case import (
    DefaultExecuteSetupUseCase,
)


class ExecutePipelineUseCase:
    """Responsável por executar uma Pipeline."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        pipeline_factory: PipelineFactory,
        execute_setup_use_case: DefaultExecuteSetupUseCase | None = None,
    ) -> None:
        self.__project_repository = project_repository
        self.__pipeline_factory = pipeline_factory
        self.__execute_setup_use_case = execute_setup_use_case

    def execute(
        self,
        project_id: str,
        environment_id: str | None = None,
        version: str | None = None,
        revision: int | None = None,
    ) -> PipelineResult:
        """Executa a Pipeline e, quando solicitado, gera o Setup."""

        project = self.__project_repository.get_by_id(
            project_id,
        )

        if project is None:
            raise ProjectNotFoundException(
                f"Projeto '{project_id}' não encontrado."
            )

        context = PipelineContext()
        context.variables["project"] = project
        context.variables["project_id"] = project.id

        pipeline = self.__pipeline_factory.create(
            project,
        )

        runner = PipelineRunner()
        result = runner.execute(
            pipeline=pipeline,
            context=context,
        )

        if (
            not result.success
            or self.__execute_setup_use_case is None
            or environment_id is None
        ):
            return result

        setup_request = SetupRequest(
            project_id=project_id,
            environment_id=environment_id,
            version=version,
            revision=revision,
            run_build=False,
        )

        setup_result = self.__execute_setup_use_case.execute(
            setup_request,
        )

        result.steps.extend(setup_result.steps)

        if not setup_result.success:
            result.success = False
            result.failed_step = "Setup"
            result.message = setup_result.message
            return result

        result.artifacts.append(setup_result.output_msi) if setup_result.output_msi else None

        return result
