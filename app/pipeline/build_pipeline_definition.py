"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_pipeline_definition.py
Descrição : Define a Pipeline padrão de Build.
--------------------------------------------------------------------
"""

from app.abstractions.process_service import ProcessService

from app.pipeline.steps.restore_step import RestoreStep
from app.pipeline.steps.build_step import BuildStep
from app.pipeline.steps.publish_step import PublishStep


class BuildPipelineDefinition:
    """
    Responsável por definir as Steps da Pipeline padrão.
    """

    def __init__(
        self,
        process_service: ProcessService,
    ) -> None:

        self.__process_service = process_service

    def create_steps(
        self,
    ) -> list:

        return [

            RestoreStep(
                process_service=self.__process_service,
            ),

            BuildStep(
                process_service=self.__process_service,
            ),

            PublishStep(
                process_service=self.__process_service,
            ),

        ]