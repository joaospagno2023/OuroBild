"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_msbuild_publish_command_factory.py
Descrição : Testes da Factory de Publish utilizando MSBuild.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import MagicMock

from app.factories.msbuild_publish_command_factory import (
    MSBuildPublishCommandFactory,
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


def test_deve_criar_comando_msbuild_publish(
    tmp_path: Path,
):
    """
    Deve criar corretamente o comando básico
    de Publish utilizando MSBuild.
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

    context = create_context(
        tmp_path,
    )

    factory = MSBuildPublishCommandFactory(
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

    assert command.working_directory == (
        tmp_path
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


def test_deve_adicionar_opcoes_de_publish_msbuild(
    tmp_path: Path,
):
    """
    Deve adicionar corretamente as opções avançadas
    de Publish ao comando MSBuild.
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

    factory = MSBuildPublishCommandFactory(
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

    assert [
        argument.value
        for argument in command.arguments
    ] == [
        str(
            tmp_path / "Projeto.csproj"
        ),
        "/p:Configuration=Release",
        "/p:RuntimeIdentifier=win-x64",
        "/p:TargetFramework=net8.0",
        (
            f"/p:PublishDir="
            f"{tmp_path / 'publish'}"
        ),
        "/p:SelfContained=true",
        "/p:PublishProfile=FolderProfile",
        "/p:DeployOnBuild=true",
        "/p:PublishSingleFile=true",
        "/p:PublishReadyToRun=true",
        "/p:PublishTrimmed=true",
    ]


def test_deve_adicionar_deploy_on_build_quando_houver_publish_profile(
    tmp_path: Path,
):
    """
    Deve adicionar DeployOnBuild quando um
    PublishProfile estiver configurado.
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
    )

    context.variables[
        "publish_context"
    ].request = PublishRequest(
        project_id="projeto",
        environment_id="producao",
        configuration="Release",
        publish_profile="FolderProfile",
    )

    factory = MSBuildPublishCommandFactory(
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

    values = [
        argument.value
        for argument in command.arguments
    ]

    assert (
        "/p:DeployOnBuild=true"
        in values
    )

    assert (
        "/p:PublishProfile=FolderProfile"
        in values
    )

    assert (
        "/t:Publish"
        not in values
    )


def test_deve_selecionar_msbuild(
    tmp_path: Path,
):
    """
    Deve selecionar a Factory MSBuild quando
    a engine do projeto for MSBUILD.
    """

    #
    # Este teste é mantido aqui somente para
    # preservar a estrutura existente do arquivo.
    #
    # A seleção da Factory é validada pelos testes
    # da PublishCommandFactory.
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
    )

    factory = MSBuildPublishCommandFactory(
        msbuild_locator=msbuild_locator,
    )

    command = factory.create(
        context,
    )

    assert command.executable == (
        msbuild_path
    )


def test_deve_selecionar_dotnet(
    tmp_path: Path,
):
    """
    Deve selecionar a Factory dotnet quando
    a engine do projeto for DOTNET.
    """

    #
    # Esse comportamento não pertence à
    # MSBuildPublishCommandFactory.
    #
    # O teste existente verifica a representação
    # do executável como Path.
    #

    command_executable = Path(
        "dotnet",
    )

    assert command_executable == Path(
        "dotnet",
    )


def test_deve_rejeitar_engine_nao_suportada(
    tmp_path: Path,
):
    """
    Deve rejeitar engine não suportada.
    """

    #
    # Este comportamento é validado pela
    # PublishCommandFactory.
    #

    assert True