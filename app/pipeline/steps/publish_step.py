"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_step.py
Descrição : Etapa responsável pela execução do Publish via MSBuild.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.process_service import (
    ProcessService,
)
from app.models.pipeline.pipeline_context import (
    PipelineContext,
)
from app.models.process.command_argument import (
    CommandArgument,
)
from app.parsers.publish.publish_parser import (
    PublishParser,
)
from app.pipeline.steps.process_step import (
    ProcessStep,
)
from app.services.msbuild_locator import (
    MSBuildLocator,
)


class PublishStep(ProcessStep):
    """
    Executa a etapa de Publish utilizando MSBuild.
    """

    @property
    def name(
        self,
    ) -> str:
        return "Publish"

    def __init__(
        self,
        process_service: ProcessService,
        msbuild_locator: MSBuildLocator,
    ) -> None:

        super().__init__(
            process_service=process_service,
        )

        self.__msbuild_locator = (
            msbuild_locator
        )

    def get_executable(
        self,
        context: PipelineContext,
    ) -> Path:
        """
        Retorna o MSBuild utilizado pelo Visual Studio.
        """

        return (
            self.__msbuild_locator.get_msbuild_path()
        )

    def get_working_directory(
        self,
        context: PipelineContext,
    ) -> Path:

        publish_context = (
            context.variables["publish_context"]
        )

        return (
            publish_context.paths.project_file.parent
        )

    def get_arguments(
        self,
        context: PipelineContext,
    ) -> list[CommandArgument]:

        publish_context = (
            context.variables["publish_context"]
        )

        request = publish_context.request

        arguments: list[CommandArgument] = [

            CommandArgument(
                value=str(
                    publish_context.paths.project_file
                ),
            ),

            CommandArgument(
                value="/t:Publish",
            ),

            CommandArgument(
                value=(
                    f"/p:Configuration="
                    f"{request.configuration}"
                ),
            ),
        ]

        #
        # Runtime
        #

        if request.runtime:

            arguments.extend(
                [
                    CommandArgument(
                        value=(
                            f"/p:RuntimeIdentifier="
                            f"{request.runtime}"
                        ),
                    ),
                ]
            )

        #
        # Framework
        #

        if request.framework:

            arguments.extend(
                [
                    CommandArgument(
                        value=(
                            f"/p:TargetFramework="
                            f"{request.framework}"
                        ),
                    ),
                ]
            )

        #
        # Pasta de saída
        #

        if request.output_directory:

            arguments.extend(
                [
                    CommandArgument(
                        value=(
                            f"/p:PublishDir="
                            f"{request.output_directory}"
                        ),
                    ),
                ]
            )

        #
        # Self Contained
        #

        if request.self_contained:

            arguments.append(
                CommandArgument(
                    value=(
                        "/p:SelfContained=true"
                    ),
                )
            )

        #
        # Publish Profile
        #

        if request.publish_profile:

            arguments.append(
                CommandArgument(
                    value=(
                        f"/p:PublishProfile="
                        f"{request.publish_profile}"
                    ),
                )
            )

        #
        # Single File
        #

        if request.single_file:

            arguments.append(
                CommandArgument(
                    value=(
                        "/p:PublishSingleFile=true"
                    ),
                )
            )

        #
        # ReadyToRun
        #

        if request.ready_to_run:

            arguments.append(
                CommandArgument(
                    value=(
                        "/p:PublishReadyToRun=true"
                    ),
                )
            )

        #
        # Trimmed
        #

        if request.trimmed:

            arguments.append(
                CommandArgument(
                    value=(
                        "/p:PublishTrimmed=true"
                    ),
                )
            )

        return arguments

    def get_output_parser(
        self,
    ):
        """
        Retorna o parser responsável por interpretar
        a saída do processo de Publish.
        """

        return PublishParser()