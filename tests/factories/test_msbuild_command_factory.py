"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_msbuild_command_factory.py
Descrição : Testes da Factory de comandos MSBuild.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import MagicMock

from app.factories.msbuild_command_factory import (
    MSBuildCommandFactory,
)

from app.models.build.build_context import (
    BuildContext,
)

from app.models.process.command import (
    Command,
)


def test_deve_criar_comando_msbuild():
    """
    Deve criar corretamente um comando MSBuild.
    """

    #
    # Arrange
    #

    msbuild_path = Path(
        r"C:\Program Files\Microsoft Visual Studio\2022\MSBuild\Current\Bin\MSBuild.exe"
    )

    msbuild_locator = MagicMock()

    msbuild_locator.get_msbuild_path.return_value = (
        msbuild_path
    )

    context = BuildContext()

    project_file = Path(
        r"C:\Projetos\Teste\Teste.csproj"
    )

    context.paths.project_file = (
        project_file
    )

    context.project = MagicMock()

    context.project.configuration = (
        "Release"
    )

    context.project.platform = (
        "AnyCPU"
    )

    #
    # Act
    #

    factory = MSBuildCommandFactory(
        msbuild_locator=msbuild_locator,
    )

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

    assert command.executable == (
        msbuild_path
    )

    assert command.working_directory == (
        project_file.parent
    )

    assert [
        argument.value
        for argument in command.arguments
    ] == [
        "Teste.csproj",
        "/p:Configuration=Release",
        "/p:Platform=AnyCPU",
        "/restore",
    ]

    msbuild_locator.get_msbuild_path.assert_called_once_with()