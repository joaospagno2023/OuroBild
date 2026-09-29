"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_pipeline_definition.py
Descrição : Define a Pipeline padrão de Build.
--------------------------------------------------------------------
"""

import os

from app.abstractions.process_service import (
    ProcessService,
)

from app.factories.publish_command_factory import (
    PublishCommandFactory,
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

from app.pipeline.steps.clean_step import (
    CleanStep,
)

from app.pipeline.steps.publish_step import (
    PublishStep,
)

from app.pipeline.steps.restore_step import (
    RestoreStep,
)

from app.pipeline.steps.source_control_step import (
    SourceControlStep,
)

from app.services.source_control_service import (
    SourceControlService,
)

from app.services.msbuild_locator import (
    MSBuildLocator,
)

from app.services.project_metadata_service import (
    ProjectMetadataService,
)


class BuildPipelineDefinition:
    """
    Responsável por definir as Steps da Pipeline padrão.
    """

    def __init__(
        self,
        process_service: ProcessService,
        msbuild_locator: MSBuildLocator,
        project_metadata_service: ProjectMetadataService,
        source_control_service: SourceControlService | None = None,
    ) -> None:

        self.__process_service = (
            process_service
        )

        self.__msbuild_locator = (
            msbuild_locator
        )

        self.__project_metadata_service = (
            project_metadata_service
        )

        self.__source_control_service = (
            source_control_service
        )

        self.__publish_command_factory = (
            PublishCommandFactory(
                msbuild_locator=(
                    self.__msbuild_locator
                ),
            )
        )

    @staticmethod
    def __clean_before_build_enabled() -> bool:
        """
        Define se o CleanStep deve rodar antes do Build.

        Por padrão NÃO roda: o Clean apaga os artefatos
        incrementais e força recompilação total a cada
        execução. Para restaurar o comportamento antigo,
        defina a variável de ambiente
        OUROBUILD_CLEAN_BEFORE_BUILD=1.
        """

        return os.environ.get(
            "OUROBUILD_CLEAN_BEFORE_BUILD",
            "0",
        ).strip().lower() in (
            "1",
            "true",
            "yes",
            "sim",
        )

    def create_steps(
        self,
        project: Project,
    ) -> list[PipelineStep]:
        """
        Cria as Steps da Pipeline.
        """

        steps = []

        if self.__source_control_service is not None:
            steps.append(
                SourceControlStep(
                    process_service=(
                        self.__process_service
                    ),
                    source_control_service=(
                        self.__source_control_service
                    ),
                )
            )

        steps.append(
            RestoreStep(
                process_service=(
                    self.__process_service
                ),
                msbuild_locator=(
                    self.__msbuild_locator
                ),
                project_metadata_service=(
                    self.__project_metadata_service
                ),
            )
        )

        if (
            project.publish_profile
            and self.__clean_before_build_enabled()
        ):

            steps.append(
                CleanStep(
                    process_service=(
                        self.__process_service
                    ),
                    msbuild_locator=(
                        self.__msbuild_locator
                    ),
                )
            )

        steps.extend(
            [

                BuildStep(
                    process_service=(
                        self.__process_service
                    ),
                    msbuild_locator=(
                        self.__msbuild_locator
                    ),
                ),

                PublishStep(
                    process_service=(
                        self.__process_service
                    ),
                    publish_command_factory=(
                        self.__publish_command_factory
                    ),
                ),
            ]
        )

        return steps