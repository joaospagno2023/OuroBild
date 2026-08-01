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
from app.pipeline.runner.pipeline_runner import PipelineRunner

class ExecutePipelineUseCase:
    """
    Responsável por executar uma Pipeline.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        pipeline_factory: PipelineFactory,
    ) -> None:
        self.__project_repository = project_repository
        self.__pipeline_factory = pipeline_factory

    def execute(
        self,
        project_id: str,
    ) -> PipelineResult:
        """
        Executa a Pipeline de um projeto.
        """

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

        pipeline = self.__pipeline_factory.create(
            project,
        )   

        return runner.execute(
            pipeline=pipeline,
            context=context,
        )