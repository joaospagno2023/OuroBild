"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_path_resolver.py
Descrição : Testes do SetupPathResolver.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.models.build.compilation_engine import (
    CompilationEngine,
)

from app.models.build.compilation_target import (
    CompilationTarget,
)

from app.models.project.project import (
    Project,
)

from app.models.project.project_type import (
    ProjectType,
)

from app.models.setup.setup_paths import (
    SetupPaths,
)

from app.services.setup.setup_path_resolver import (
    SetupPathResolver,
)


def create_project(
    publish_path: str,
    output_msi: str = "Teste.msi",
    aip_path: str = r"Setup\Teste.aip",
) -> Project:
    """
    Cria um projeto mínimo para os testes.
    """

    return Project(
        id="teste",
        name="Projeto Teste",
        description="Projeto utilizado nos testes.",

        type=ProjectType.CLIENT,

        solution_path=None,
        project_path="Projeto.csproj",

        compilation_target=(
            CompilationTarget.PROJECT
        ),

        compilation_engine=(
            CompilationEngine.MSBUILD
        ),

        publish_path=publish_path,
        aip_path=aip_path,
        output_msi=output_msi,
        network_path="",
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )


def create_paths(
    tmp_path: Path,
) -> dict:
    """
    Cria as raízes utilizadas pelo resolver.
    """

    return {
        "project_root": (
            tmp_path
            / "Projeto"
        ),
        "workspace_root": (
            tmp_path
            / "Workspace"
        ),
        "installer_root": (
            tmp_path
            / "Installer"
        ),
        "aip_root": (
            tmp_path
            / "AIPs"
        ),
    }


def test_deve_resolver_publish_path_relativo(
    tmp_path: Path,
):
    """
    Deve resolver publish_path relativo
    à pasta do projeto.
    """

    project = create_project(
        r"bin\Release\net8.0\publish",
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        **paths,
    )

    assert result.publish_path == (
        paths["project_root"]
        / "bin"
        / "Release"
        / "net8.0"
        / "publish"
    )


def test_deve_respeitar_publish_path_absoluto(
    tmp_path: Path,
):
    """
    Deve respeitar publish_path absoluto.
    """

    publish_path = (
        tmp_path
        / "Publish"
        / "Projeto"
    )

    project = create_project(
        str(publish_path),
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        **paths,
    )

    assert result.publish_path == (
        publish_path
    )


def test_deve_criar_installer_path(
    tmp_path: Path,
):
    """
    Deve criar automaticamente o diretório
    de saída dos instaladores.
    """

    project = create_project(
        "bin",
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        **paths,
    )

    assert result.setup_output_path == (
        paths["installer_root"]
    )

    assert result.setup_output_path.exists()


def test_deve_usar_output_msi(
    tmp_path: Path,
):
    """
    Deve utilizar output_msi como nome do MSI.
    """

    project = create_project(
        "bin",
        output_msi="OuroNetApi.msi",
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        **paths,
    )

    assert result.output_msi == (
        paths["installer_root"]
        / "OuroNetApi.msi"
    )


def test_deve_resolver_aip_relativo(
    tmp_path: Path,
):
    """
    Deve resolver aip_path relativo à raiz
    central dos projetos Advanced Installer.
    """

    project = create_project(
        "bin",
        aip_path=r"Setup\OuroNet.aip",
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        **paths,
    )

    assert result.aip_path == (
        paths["aip_root"]
        / "Setup"
        / "OuroNet.aip"
    )


def test_deve_respeitar_aip_path_absoluto(
    tmp_path: Path,
):
    """
    Deve respeitar aip_path absoluto.
    """

    aip_path = (
        tmp_path
        / "AIPs"
        / "OuroNet.aip"
    )

    project = create_project(
        "bin",
        aip_path=str(aip_path),
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        **paths,
    )

    assert result.aip_path == (
        aip_path
    )


def test_deve_rejeitar_publish_path_vazio(
    tmp_path: Path,
):
    """
    Deve rejeitar publish_path vazio.
    """

    project = create_project(
        "",
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    with pytest.raises(
        ValueError,
        match="não possui publish_path configurado",
    ):
        resolver.resolve(
            project=project,
            **paths,
        )


def test_deve_rejeitar_output_msi_vazio(
    tmp_path: Path,
):
    """
    Deve rejeitar output_msi vazio.
    """

    project = create_project(
        "bin",
        output_msi="",
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    with pytest.raises(
        ValueError,
        match="não possui output_msi configurado",
    ):
        resolver.resolve(
            project=project,
            **paths,
        )


def test_deve_rejeitar_aip_path_vazio(
    tmp_path: Path,
):
    """
    Deve rejeitar aip_path vazio.
    """

    project = create_project(
        "bin",
        aip_path="",
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    with pytest.raises(
        ValueError,
        match="não possui aip_path configurado",
    ):
        resolver.resolve(
            project=project,
            **paths,
        )


def test_deve_rejeitar_aip_root_nao_informado(
    tmp_path: Path,
):
    """
    Deve rejeitar a resolução quando a raiz dos AIPs
    não for informada.
    """

    project = create_project(
        "bin",
    )

    paths = create_paths(
        tmp_path,
    )

    paths["aip_root"] = None

    resolver = SetupPathResolver()

    with pytest.raises(
        ValueError,
        match="raiz dos projetos Advanced Installer",
    ):
        resolver.resolve(
            project=project,
            **paths,
        )


def test_deve_resolver_setup_output_path_para_cliente(
    tmp_path: Path,
):
    """
    Deve criar o diretório de saída do Setup
    para um projeto do tipo Cliente.
    """

    project = create_project(
        "bin",
    )

    project.type = (
        ProjectType.CLIENT
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        version="10.4",
        revision=5,
        **paths,
    )

    assert result.setup_output_path == (
        paths["installer_root"]
        / "10.4.5"
        / "Cliente"
    )


def test_deve_resolver_setup_output_path_para_server(
    tmp_path: Path,
):
    """
    Deve criar o diretório de saída do Setup
    para um projeto do tipo Server.
    """

    project = create_project(
        "bin",
    )

    project.type = (
        ProjectType.SERVER
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        version="10.4",
        revision=5,
        **paths,
    )

    assert result.setup_output_path == (
        paths["installer_root"]
        / "10.4.5"
        / "Server"
    )


def test_deve_resolver_output_msi_dentro_da_pasta_do_tipo(
    tmp_path: Path,
):
    """
    Deve colocar o MSI dentro do diretório
    correspondente ao tipo do projeto.
    """

    project = create_project(
        "bin",
        output_msi="LinkPagamento.msi",
    )

    project.type = (
        ProjectType.CLIENT
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        version="10.4",
        revision=5,
        **paths,
    )

    assert result.output_msi == (
        paths["installer_root"]
        / "10.4.5"
        / "Cliente"
        / "LinkPagamento.msi"
    )


def test_deve_compor_versao_com_revision(
    tmp_path: Path,
):
    """
    Deve combinar versão e revisão para formar
    o diretório da versão do Setup.
    """

    project = create_project(
        "bin",
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        version="10.4",
        revision=12,
        **paths,
    )

    assert result.setup_output_path == (
        paths["installer_root"]
        / "10.4.12"
        / "Cliente"
    )


def test_deve_resolver_visualstudio_setup_path_relativo(
    tmp_path: Path,
):
    """
    Deve resolver o caminho do projeto de Setup
    do Visual Studio relativo à raiz do workspace.
    """

    project = create_project(
        "bin",
    )

    project.visualstudio_setup_path = (
        "04-Setup\\"
        "OuroNet.Client.WinServiceLinkPagamento.Setup\\"
        "OuroNet.Client.WinServiceLinkPagamento.Setup.vdproj"
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        **paths,
    )

    assert result.visualstudio_setup_path == (
        paths["workspace_root"]
        / "04-Setup"
        / "OuroNet.Client.WinServiceLinkPagamento.Setup"
        / "OuroNet.Client.WinServiceLinkPagamento.Setup.vdproj"
    )


def test_deve_respeitar_visualstudio_setup_path_absoluto(
    tmp_path: Path,
):
    """
    Deve respeitar visualstudio_setup_path absoluto.
    """

    visualstudio_setup_path = (
        tmp_path
        / "Setup"
        / "Teste.vdproj"
    )

    project = create_project(
        "bin",
    )

    project.visualstudio_setup_path = (
        str(visualstudio_setup_path)
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        **paths,
    )

    assert result.visualstudio_setup_path == (
        visualstudio_setup_path
    )


def test_deve_retornar_none_quando_visualstudio_setup_path_nao_for_configurado(
    tmp_path: Path,
):
    """
    Deve retornar None quando o projeto não possuir
    Setup do Visual Studio configurado.
    """

    project = create_project(
        "bin",
    )

    project.visualstudio_setup_path = None

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        **paths,
    )

    assert result.visualstudio_setup_path is None


def test_deve_criar_aip_root_quando_nao_existir(
    tmp_path: Path,
):
    """
    Deve criar a raiz central dos projetos AIP quando
    ela ainda não existir.
    """

    project = create_project(
        "bin",
    )

    paths = create_paths(
        tmp_path,
    )

    aip_root = paths["aip_root"]

    assert not aip_root.exists()

    resolver = SetupPathResolver()

    resolver.resolve(
        project=project,
        **paths,
    )

    assert aip_root.exists()


def test_deve_manter_aip_dentro_da_raiz_central(
    tmp_path: Path,
):
    """
    Deve manter um AIP relativo dentro da raiz central
    dos projetos Advanced Installer.
    """

    project = create_project(
        "bin",
        aip_path="LinkPagamento.aip",
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        **paths,
    )

    assert result.aip_path.parent == (
        paths["aip_root"]
    )

    assert result.aip_path == (
        paths["aip_root"]
        / "LinkPagamento.aip"
    )


def test_deve_permitir_aip_em_subdiretorio_da_raiz_central(
    tmp_path: Path,
):
    """
    Deve permitir que o AIP esteja em um subdiretório
    da raiz central.
    """

    project = create_project(
        "bin",
        aip_path=(
            r"OuroNet\LinkPagamento.aip"
        ),
    )

    paths = create_paths(
        tmp_path,
    )

    resolver = SetupPathResolver()

    result = resolver.resolve(
        project=project,
        **paths,
    )

    assert result.aip_path == (
        paths["aip_root"]
        / "OuroNet"
        / "LinkPagamento.aip"
    )