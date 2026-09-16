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
from app.services.project_metadata_service import (
    ProjectMetadataService,
)

from app.services.source_control_service import (
    SourceControlService,
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
        project_metadata_service: ProjectMetadataService,
        source_control_service: SourceControlService | None = None,
    ) -> None:

        self.__definition = (
            BuildPipelineDefinition(
                process_service=process_service,
                msbuild_locator=msbuild_locator,
                project_metadata_service=(
                    project_metadata_service
                ),
                source_control_service=(
                    source_control_service
                ),
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