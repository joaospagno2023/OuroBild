"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_step.py
Descrição : Etapa responsável pela execução do Publish.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.process_service import (
    ProcessService,
)

from app.factories.publish_command_factory import (
    PublishCommandFactory,
)

from app.models.pipeline.pipeline_context import (
    PipelineContext,
)

from app.models.process.command_argument import (
    CommandArgument,
)

from app.pipeline.steps.process_step import (
    ProcessStep,
)


class PublishStep(
    ProcessStep,
):
    """
    Executa a etapa de Publish.
    """

    @property
    def name(
        self,
    ) -> str:
        return "Publish"

    def __init__(
        self,
        process_service: ProcessService,
        publish_command_factory: PublishCommandFactory,
    ) -> None:
        """
        Inicializa a Step.
        """

        super().__init__(
            process_service=process_service,
        )

        self.__publish_command_factory = (
            publish_command_factory
        )

    def __get_command(
        self,
        context: PipelineContext,
    ):
        """
        Obtém o Command através da Factory.
        """

        return (
            self.__publish_command_factory.create(
                context,
            )
        )

    def get_executable(
        self,
        context: PipelineContext,
    ) -> Path:
        """
        Retorna o executável definido pelo CommandFactory.
        """

        command = self.__get_command(
            context,
        )

        return command.executable

    def get_working_directory(
        self,
        context: PipelineContext,
    ) -> Path:
        """
        Retorna o diretório de trabalho definido
        pelo CommandFactory.
        """

        command = self.__get_command(
            context,
        )

        return command.working_directory

    def get_arguments(
        self,
        context: PipelineContext,
    ) -> list[CommandArgument]:
        """
        Retorna os argumentos definidos pelo
        CommandFactory.
        """

        command = self.__get_command(
            context,
        )

        return command.arguments