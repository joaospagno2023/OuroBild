"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_dotnet_publish_command_factory.py
Descrição : Testes da Factory de Publish utilizando dotnet.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.factories.dotnet_publish_command_factory import (
    DotnetPublishCommandFactory,
)

from app.models.pipeline.pipeline_context import (
    PipelineContext,
)

from app.models.publish.publish_context import (
    PublishContext,
)

from app.models.publish.publish_request import (
    PublishRequest,
)


def create_context(
    tmp_path: Path,
) -> PipelineContext:
    """
    Cria um PipelineContext mínimo para os testes.
    """

    context = PipelineContext()

    publish_context = PublishContext()

    publish_context.request = PublishRequest(
        project_id="projeto",
        environment_id="producao",
        configuration="Release",
    )

    publish_context.paths.project_file = (
        tmp_path / "Projeto.csproj"
    )

    context.variables["publish_context"] = (
        publish_context
    )

    return context


def test_deve_criar_comando_dotnet_publish(
    tmp_path: Path,
):
    """
    Deve criar corretamente o comando básico
    de dotnet publish.
    """

    #
    # Arrange
    #

    context = create_context(
        tmp_path,
    )

    factory = DotnetPublishCommandFactory()

    #
    # Act
    #

    command = factory.create(
        context,
    )

    #
    # Assert
    #

    assert command.executable == Path(
        "dotnet",
    )

    assert command.working_directory == (
        tmp_path
    )

    assert [
        argument.value
        for argument in command.arguments
    ] == [
        "publish",
        "Projeto.csproj",
        "--configuration",
        "Release",
        "--no-build",
    ]


def test_deve_adicionar_opcoes_de_publish_dotnet(
    tmp_path: Path,
):
    """
    Deve adicionar corretamente as opções
    avançadas de dotnet publish.
    """

    #
    # Arrange
    #

    context = create_context(
        tmp_path,
    )

    context.variables[
        "publish_context"
    ].request = PublishRequest(
        project_id="projeto",
        environment_id="producao",
        configuration="Release",
        runtime="win-x64",
        framework="net8.0",
        output_directory=(
            str(tmp_path / "publish")
        ),
        self_contained=True,
        publish_profile="FolderProfile",
        single_file=True,
        ready_to_run=True,
        trimmed=True,
    )

    factory = DotnetPublishCommandFactory()

    #
    # Act
    #

    command = factory.create(
        context,
    )

    #
    # Assert
    #

    assert [
        argument.value
        for argument in command.arguments
    ] == [
        "publish",
        "Projeto.csproj",
        "--configuration",
        "Release",
        "--no-build",
        "--runtime",
        "win-x64",
        "--framework",
        "net8.0",
        "--output",
        str(tmp_path / "publish"),
        "--self-contained",
        "/p:PublishProfile=FolderProfile",
        "/p:PublishSingleFile=true",
        "/p:PublishReadyToRun=true",
        "/p:PublishTrimmed=true",
    ]