"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_command_factory.py
Descrição : Factory responsável por selecionar a implementação de Publish conforme a engine de compilação.
--------------------------------------------------------------------
"""

from app.factories.dotnet_publish_command_factory import (
    DotnetPublishCommandFactory,
)

from app.factories.msbuild_publish_command_factory import (
    MSBuildPublishCommandFactory,
)

from app.models.build.compilation_engine import (
    CompilationEngine,
)

from app.models.pipeline.pipeline_context import (
    PipelineContext,
)

from app.models.process.command import (
    Command,
)

from app.services.msbuild_locator import (
    MSBuildLocator,
)


class PublishCommandFactory:
    """
    Seleciona a Factory responsável por criar
    o comando de Publish.
    """

    def __init__(
        self,
        msbuild_locator: MSBuildLocator,
    ) -> None:
        """
        Inicializa a Factory.
        """

        self.__msbuild_factory = (
            MSBuildPublishCommandFactory(
                msbuild_locator=msbuild_locator,
            )
        )

        self.__dotnet_factory = (
            DotnetPublishCommandFactory()
        )

    def create(
        self,
        context: PipelineContext,
    ) -> Command:
        """
        Cria o comando de Publish conforme
        a engine de compilação do projeto.
        """

        publish_context = (
            context.variables["publish_context"]
        )

        project = (
            publish_context.project
        )

        if project is None:

            raise ValueError(
                "Projeto não informado no PublishContext."
            )

        engine = (
            project.compilation_engine
        )

        if engine == CompilationEngine.MSBUILD:

            return self.__msbuild_factory.create(
                context,
            )

        if engine == CompilationEngine.DOTNET:

            return self.__dotnet_factory.create(
                context,
            )

        raise ValueError(
            f"Engine de compilação não suportada: "
            f"{engine}"
        )