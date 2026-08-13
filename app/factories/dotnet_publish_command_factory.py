"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : dotnet_publish_command_factory.py
Descrição : Factory responsável por criar comandos de Publish
            utilizando a CLI do .NET.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.pipeline.pipeline_context import (
    PipelineContext,
)

from app.models.process.command import (
    Command,
)

from app.models.process.command_argument import (
    CommandArgument,
)


class DotnetPublishCommandFactory:
    """
    Responsável por montar o comando de Publish
    utilizando a CLI do .NET.
    """

    def create(
        self,
        context: PipelineContext,
    ) -> Command:
        """
        Cria o comando dotnet publish.
        """

        publish_context = (
            context.variables["publish_context"]
        )

        request = (
            publish_context.request
        )

        project_file = (
            publish_context.paths.project_file
        )

        #
        # Argumentos básicos
        #

        arguments: list[CommandArgument] = [

            CommandArgument(
                value="publish",
            ),

            CommandArgument(
                value=project_file.name,
            ),

            CommandArgument(
                value="--configuration",
            ),

            CommandArgument(
                value=request.configuration,
            ),

            #
            # Nunca recompila.
            #

            CommandArgument(
                value="--no-build",
            ),
        ]

        #
        # Runtime
        #

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

        #
        # Framework
        #

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

        #
        # Pasta de saída
        #

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

        #
        # Self Contained
        #

        if request.self_contained:

            arguments.append(
                CommandArgument(
                    value="--self-contained",
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

        return Command(
            executable=Path(
                "dotnet",
            ),
            working_directory=(
                project_file.parent
            ),
            arguments=arguments,
        )