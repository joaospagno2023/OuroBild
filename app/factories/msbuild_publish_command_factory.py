"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : msbuild_publish_command_factory.py
Descrição : Factory responsável por criar comandos de Publish utilizando o MSBuild.
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

from app.services.msbuild_locator import (
    MSBuildLocator,
)


class MSBuildPublishCommandFactory:
    """
    Responsável por montar o comando de Publish
    utilizando o MSBuild.
    """

    def __init__(
        self,
        msbuild_locator: MSBuildLocator,
    ) -> None:
        """
        Inicializa a Factory.
        """

        self.__msbuild_locator = (
            msbuild_locator
        )

    def create(
        self,
        context: PipelineContext,
    ) -> Command:
        """
        Cria o comando MSBuild de Publish.
        """

        publish_context = (
            context.variables["publish_context"]
        )

        request = (
            publish_context.request
        )

        #
        # Executável
        #

        executable = (
            self.__msbuild_locator.get_msbuild_path()
        )

        #
        # Argumentos
        #
        # A ordem é importante:
        #
        # 1. Projeto
        # 2. Propriedades /p:*
        # 3. Target /t:Publish
        #

        arguments: list[CommandArgument] = [

            CommandArgument(
                value=str(
                    publish_context.paths.project_file
                ),
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

            arguments.append(
                CommandArgument(
                    value=(
                        f"/p:RuntimeIdentifier="
                        f"{request.runtime}"
                    ),
                )
            )

        #
        # Framework
        #

        if request.framework:

            arguments.append(
                CommandArgument(
                    value=(
                        f"/p:TargetFramework="
                        f"{request.framework}"
                    ),
                )
            )

        #
        # Pasta de saída
        #

        if request.output_directory:

            arguments.append(
                CommandArgument(
                    value=(
                        f"/p:PublishDir="
                        f"{request.output_directory}"
                    ),
                )
            )

        #
        # Self Contained
        #

        if request.self_contained:

            arguments.append(
                CommandArgument(
                    value="/p:SelfContained=true",
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
            # Quando utilizamos PublishProfile,
            # habilitamos o DeployOnBuild.
            #

            arguments.append(
                CommandArgument(
                    value="/p:DeployOnBuild=true",
                )
            )

        #
        # Single File
        #

        if request.single_file:

            arguments.append(
                CommandArgument(
                    value="/p:PublishSingleFile=true",
                )
            )

        #
        # ReadyToRun
        #

        if request.ready_to_run:

            arguments.append(
                CommandArgument(
                    value="/p:PublishReadyToRun=true",
                )
            )

        #
        # Trimmed
        #

        if request.trimmed:

            arguments.append(
                CommandArgument(
                    value="/p:PublishTrimmed=true",
                )
            )

        #
        # Target
        #
        # Quando existe PublishProfile, o MSBuild utiliza
        # o DeployOnBuild e não devemos adicionar
        # explicitamente o target /t:Publish.
        #

        if not request.publish_profile:

            arguments.append(
                CommandArgument(
                    value="/t:Publish",
                )
            )

        #
        # Resultado
        #

        return Command(
            executable=executable,
            working_directory=(
                publish_context.paths.project_file.parent
            ),
            arguments=arguments,
        )