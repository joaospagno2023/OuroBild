"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_pipeline_definition.py
Descrição : Define a Pipeline padrão de Build.
--------------------------------------------------------------------
"""

from app.abstractions.process_service import (
    ProcessService,
)
from app.models.project.project import (
    Project,
)
from app.pipeline.abstractions.pipeline_step import (
    PipelineStep,
)
from app.pipeline.steps.build_step import (
    BuildStep,
)
from app.pipeline.steps.publish_step import (
    PublishStep,
)
from app.pipeline.steps.restore_step import (
    RestoreStep,
)


class BuildPipelineDefinition:
    """
    Responsável por definir as Steps da Pipeline.
    """

    def __init__(
        self,
        process_service: ProcessService,
    ) -> None:

        self.__process_service = (
            process_service
        )

    def create_steps(
        self,
        project: Project,
    ) -> list[PipelineStep]:
        """
        Cria as Steps da Pipeline conforme a configuração
        do projeto.
        """

        steps: list[PipelineStep] = []

        #
        # Restore
        #

        if project.pipeline.restore:

            steps.append(

                RestoreStep(
                    process_service=self.__process_service,
                )

            )

        #
        # Build
        #

        if project.pipeline.build:

            steps.append(

                BuildStep(
                    process_service=self.__process_service,
                )

            )

        #
        # Publish
        #

        if project.pipeline.publish:

            steps.append(

                PublishStep(
                    process_service=self.__process_service,
                )

            )

        return steps