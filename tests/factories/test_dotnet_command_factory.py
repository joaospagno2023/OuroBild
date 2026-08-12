"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_dotnet_command_factory.py
Descrição : Testes da Factory de comandos dotnet.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.factories.dotnet_command_factory import (
    DotnetCommandFactory,
)

from app.models.build.build_context import (
    BuildContext,
)

from app.models.process.command import (
    Command,
)


def test_deve_criar_comando_dotnet():
    """
    Deve criar corretamente um comando dotnet.
    """

    #
    # Arrange
    #

    context = BuildContext()

    project_file = Path(
        r"C:\Projetos\Teste\Teste.csproj"
    )

    context.paths.project_file = (
        project_file
    )

    context.project = type(
        "ProjectMock",
        (),
        {
            "configuration": "Release",
        },
    )()

    #
    # Act
    #

    factory = DotnetCommandFactory()

    command = factory.create(
        context,
    )

    #
    # Assert
    #

    assert isinstance(
        command,
        Command,
    )

    assert command.executable == Path(
        "dotnet"
    )

    assert command.working_directory == (
        project_file.parent
    )

    assert [
        argument.value
        for argument in command.arguments
    ] == [
        "build",
        "Teste.csproj",
        "--configuration",
        "Release",
        "--no-restore",
    ]