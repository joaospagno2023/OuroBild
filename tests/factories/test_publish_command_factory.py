"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_publish_command_factory.py
Descrição : Testes da Factory responsável por selecionar
            a implementação de Publish.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.factories.publish_command_factory import (
    PublishCommandFactory,
)

from app.models.build.compilation_engine import (
    CompilationEngine,
)

from app.models.build.compilation_target import (
    CompilationTarget,
)

from app.models.pipeline.pipeline_context import (
    PipelineContext,
)

from app.models.project.project import (
    Project,
)

from app.models.publish.publish_context import (
    PublishContext,
)

from app.models.publish.publish_request import (
    PublishRequest,
)


def create_context(
    tmp_path: Path,
    engine: CompilationEngine,
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

    publish_context.project = Project(
        id="projeto",
        name="Projeto Teste",
        description="Projeto utilizado nos testes.",
        solution_path=None,
        project_path=str(
            tmp_path / "Projeto.csproj"
        ),
        compilation_target=(
            CompilationTarget.PROJECT
        ),
        compilation_engine=engine,
        publish_path=str(
            tmp_path / "publish"
        ),
        aip_path="",
        output_msi="",
        network_path="",
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )

    publish_context.paths.project_file = (
        tmp_path / "Projeto.csproj"
    )

    context.variables["publish_context"] = (
        publish_context
    )

    return context


def test_deve_selecionar_msbuild(
    tmp_path: Path,
):
    """
    Deve selecionar a Factory MSBuild quando
    a engine do projeto for MSBUILD.
    """

    #
    # Arrange
    #

    msbuild_path = Path(
        r"C:\MSBuild\MSBuild.exe"
    )

    msbuild_locator = MagicMock()

    msbuild_locator.get_msbuild_path.return_value = (
        msbuild_path
    )

    context = create_context(
        tmp_path,
        CompilationEngine.MSBUILD,
    )

    factory = PublishCommandFactory(
        msbuild_locator=msbuild_locator,
    )

    #
    # Act
    #

    command = factory.create(
        context,
    )

    #
    # Assert
    #

    assert command.executable == (
        msbuild_path
    )

    assert [
        argument.value
        for argument in command.arguments
    ] == [
        str(
            tmp_path / "Projeto.csproj"
        ),
        "/p:Configuration=Release",
        "/t:Publish",
    ]

    msbuild_locator.get_msbuild_path.assert_called_once_with()


def test_deve_selecionar_dotnet(
    tmp_path: Path,
):
    """
    Deve selecionar a Factory Dotnet quando
    a engine do projeto for DOTNET.
    """

    #
    # Arrange
    #

    msbuild_locator = MagicMock()

    context = create_context(
        tmp_path,
        CompilationEngine.DOTNET,
    )

    factory = PublishCommandFactory(
        msbuild_locator=msbuild_locator,
    )

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

    msbuild_locator.get_msbuild_path.assert_not_called()


def test_deve_rejeitar_engine_nao_suportada(
    tmp_path: Path,
):
    """
    Deve rejeitar uma engine que não pertença
    ao enum CompilationEngine.
    """

    #
    # Arrange
    #

    msbuild_locator = MagicMock()

    context = create_context(
        tmp_path,
        CompilationEngine.MSBUILD,
    )

    #
    # Substituímos a engine depois que o Project
    # foi validado pelo Pydantic.
    #

    context.variables[
        "publish_context"
    ].project.compilation_engine = (
        "engine-invalida"
    )

    factory = PublishCommandFactory(
        msbuild_locator=msbuild_locator,
    )

    #
    # Act / Assert
    #

    with pytest.raises(
        ValueError,
        match="Engine de compilação não suportada",
    ):
        factory.create(
            context,
        )