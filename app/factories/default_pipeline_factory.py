"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : default_pipeline_factory.py
Descrição : Implementação padrão da Pipeline do OuroBuild.
--------------------------------------------------------------------
"""

from app.abstractions.pipeline_factory import (
    PipelineFactory,
)
from app.abstractions.process_service import (
    ProcessService,
)
from app.models.pipeline.pipeline import (
    Pipeline,
)
from app.models.project.project import (
    Project,
)
from app.pipeline.build_pipeline_definition import (
    BuildPipelineDefinition,
)
from app.services.msbuild_locator import (
    MSBuildLocator,
)


class DefaultPipelineFactory(
    PipelineFactory,
):
    """
    Cria a Pipeline padrão do OuroBuild.
    """

    def __init__(
        self,
        process_service: ProcessService,
        msbuild_locator: MSBuildLocator,
    ) -> None:

        self.__definition = (
            BuildPipelineDefinition(
                process_service=process_service,
                msbuild_locator=msbuild_locator,
            )
        )

    def create(
        self,
        project: Project,
    ) -> Pipeline:
        """
        Cria a Pipeline padrão.
        """

        return Pipeline(

            name="Build Pipeline",

            steps=self.__definition.create_steps(
                project=project,
            ),
        )