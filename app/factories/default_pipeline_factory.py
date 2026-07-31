"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : default_pipeline_factory.py
Descrição : Implementação padrão da Pipeline do OuroBuild.
--------------------------------------------------------------------
"""

from app.abstractions.pipeline_factory import PipelineFactory
from app.abstractions.process_service import ProcessService
from app.models.pipeline.pipeline import Pipeline
from app.models.project.project import Project
from app.pipeline.steps.build_step import BuildStep
from app.pipeline.steps.restore_step import RestoreStep


class DefaultPipelineFactory(PipelineFactory):
    """
    Cria a Pipeline padrão do OuroBuild.
    """

    def __init__(
        self,
        process_service: ProcessService,
    ) -> None:
        self.__process_service = process_service

    def create(
        self,
        project: Project,
    ) -> Pipeline:
        """
        Cria a Pipeline padrão.
        """

        return Pipeline(
            name="Build Pipeline",
            steps=[
                RestoreStep(
                    process_service=self.__process_service,
                ),
                BuildStep(
                    process_service=self.__process_service,
                ),
            ],
        )