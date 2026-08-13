"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_publish_step.py
Descrição : Testes da PublishStep.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import MagicMock

from app.models.pipeline.pipeline_context import (
    PipelineContext,
)

from app.models.process.command import (
    Command,
)

from app.pipeline.steps.publish_step import (
    PublishStep,
)


def create_publish_context(
    tmp_path: Path,
):
    """
    Cria um contexto mínimo para os testes
    da PublishStep.
    """

    project_file = (
        tmp_path
        / "Projeto.csproj"
    )

    project_file.write_text(
        "<Project />",
        encoding="utf-8",
    )

    request = MagicMock()

    request.configuration = (
        "Release"
    )

    paths = MagicMock()

    paths.project_file = (
        project_file
    )

    publish_context = MagicMock()

    publish_context.request = (
        request
    )

    publish_context.paths = (
        paths
    )

    return PipelineContext(
        variables={
            "publish_context": (
                publish_context
            ),
        },
    )


def create_publish_step(
    process_service=None,
    publish_command_factory=None,
):
    """
    Cria uma PublishStep para os testes.
    """

    if process_service is None:

        process_service = MagicMock()

    if publish_command_factory is None:

        publish_command_factory = MagicMock()

    return PublishStep(
        process_service=process_service,
        publish_command_factory=(
            publish_command_factory
        ),
    )


def create_command(
    tmp_path: Path,
) -> Command:
    """
    Cria um Command de teste.
    """

    return Command(
        executable=Path(
            "dotnet",
        ),
        working_directory=(
            tmp_path
        ),
        arguments=[],
    )


def test_publish_deve_possuir_nome_publish(
    tmp_path,
):
    """
    A Step deve possuir o nome Publish.
    """

    step = create_publish_step()

    assert step.name == "Publish"


def test_publish_deve_delegar_criacao_do_comando(
    tmp_path,
):
    """
    A PublishStep deve delegar a criação do
    Command para a PublishCommandFactory.
    """

    #
    # Arrange
    #

    context = create_publish_context(
        tmp_path,
    )

    command = create_command(
        tmp_path,
    )

    factory = MagicMock()

    factory.create.return_value = (
        command
    )

    step = create_publish_step(
        publish_command_factory=factory,
    )

    #
    # Act
    #

    executable = step.get_executable(
        context,
    )

    #
    # Assert
    #

    assert executable == (
        command.executable
    )

    factory.create.assert_called_once_with(
        context,
    )


def test_publish_deve_obter_diretorio_do_comando(
    tmp_path,
):
    """
    A PublishStep deve utilizar o diretório
    retornado pelo CommandFactory.
    """

    #
    # Arrange
    #

    context = create_publish_context(
        tmp_path,
    )

    command = create_command(
        tmp_path,
    )

    factory = MagicMock()

    factory.create.return_value = (
        command
    )

    step = create_publish_step(
        publish_command_factory=factory,
    )

    #
    # Act
    #

    working_directory = (
        step.get_working_directory(
            context,
        )
    )

    #
    # Assert
    #

    assert working_directory == (
        command.working_directory
    )


def test_publish_deve_obter_argumentos_do_comando(
    tmp_path,
):
    """
    A PublishStep deve utilizar os argumentos
    retornados pelo CommandFactory.
    """

    #
    # Arrange
    #

    context = create_publish_context(
        tmp_path,
    )

    command = create_command(
        tmp_path,
    )

    factory = MagicMock()

    factory.create.return_value = (
        command
    )

    step = create_publish_step(
        publish_command_factory=factory,
    )

    #
    # Act
    #

    arguments = step.get_arguments(
        context,
    )

    #
    # Assert
    #

    assert arguments == (
        command.arguments
    )