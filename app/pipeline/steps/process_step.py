"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_step.py
Descrição : Etapa responsável pela execução do dotnet publish.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.process_service import ProcessService
from app.models.pipeline.pipeline_context import PipelineContext
from app.models.process.command_argument import CommandArgument
from app.parsers.publish.publish_parser import (
    PublishParser,
)
from app.pipeline.steps.process_step import ProcessStep


class PublishStep(ProcessStep):
    """
    Executa o comando dotnet publish.
    """

    @property
    def name(
        self,
    ) -> str:
        return "Publish"

    def __init__(
        self,
        process_service: ProcessService,
    ) -> None:

        super().__init__(
            process_service=process_service,
        )

    def get_executable(
        self,
        context: PipelineContext,
    ) -> Path:

        return Path("dotnet")

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
                value="publish",
            ),

            CommandArgument(
                value=(
                    publish_context.paths.project_file.name
                ),
            ),

            CommandArgument(
                value="--configuration",
            ),

            CommandArgument(
                value=request.configuration,
            ),

            #
            # Não recompila.
            #

            CommandArgument(
                value="--no-build",
            ),
        ]

        if request.runtime:

            arguments.extend(
                [
                    CommandArgument(
                        value="--runtime",
                    ),
                    CommandArgument(
                        value=request.runtime,
                    ),
                ]
            )

        if request.framework:

            arguments.extend(
                [
                    CommandArgument(
                        value="--framework",
                    ),
                    CommandArgument(
                        value=request.framework,
                    ),
                ]
            )

        if request.output_directory:

            arguments.extend(
                [
                    CommandArgument(
                        value="--output",
                    ),
                    CommandArgument(
                        value=request.output_directory,
                    ),
                ]
            )

        if request.self_contained:

            arguments.append(
                CommandArgument(
                    value="--self-contained",
                )
            )

        if request.publish_profile:

            arguments.append(
                CommandArgument(
                    value=(
                        f"/p:PublishProfile={request.publish_profile}"
                    ),
                )
            )

        if request.single_file:

            arguments.append(
                CommandArgument(
                    value="/p:PublishSingleFile=true",
                )
            )

        if request.ready_to_run:

            arguments.append(
                CommandArgument(
                    value="/p:PublishReadyToRun=true",
                )
            )

        if request.trimmed:

            arguments.append(
                CommandArgument(
                    value="/p:PublishTrimmed=true",
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