"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_workspace_service.py
Descrição : Testes do AdvancedInstallerWorkspaceService.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.services.setup.advanced_installer_workspace_service import (
    AdvancedInstallerWorkspaceService,
)


def create_service(
    tmp_path: Path,
) -> AdvancedInstallerWorkspaceService:
    """
    Cria o serviço de workspace utilizado pelos testes.
    """

    workspace_root = (
        tmp_path
        / ".work"
    )

    return AdvancedInstallerWorkspaceService(
        workspace_root=workspace_root,
    )


def create_workspace_path(
    tmp_path: Path,
    project_id: str = "teste",
) -> Path:
    """
    Calcula o caminho esperado do workspace do projeto.

    Estrutura:

        <tmp_path>/.work/<project_id>
    """

    return (
        tmp_path
        / ".work"
        / project_id
    )


def create_workspace_aip_path(
    tmp_path: Path,
    project_id: str = "teste",
    aip_name: str = "OuroNet.aip",
) -> Path:
    """
    Calcula o caminho esperado do AIP dentro do workspace.

    Estrutura:

        <tmp_path>/.work/<project_id>/AIP/<aip_name>
    """

    return (
        tmp_path
        / ".work"
        / project_id
        / "AIP"
        / aip_name
    )


def create_workspace_prerequisites_path(
    tmp_path: Path,
    project_id: str = "teste",
) -> Path:
    """
    Calcula o caminho esperado do Prerequisites dentro
    do workspace.

    Estrutura:

        <tmp_path>/.work/<project_id>/Prerequisites
    """

    return (
        tmp_path
        / ".work"
        / project_id
        / "Prerequisites"
    )


def create_workspace_publish_path(
    tmp_path: Path,
    project_id: str = "teste",
) -> Path:
    """
    Calcula o caminho esperado do Release dentro
    do workspace.

    Estrutura:

        <tmp_path>/.work/<project_id>/Release
    """

    return (
        tmp_path
        / ".work"
        / project_id
        / "Release"
    )


def test_deve_criar_workspace_do_projeto(
    tmp_path: Path,
):
    """
    Deve criar o workspace do projeto.
    """

    service = create_service(
        tmp_path,
    )

    workspace = service.create(
        project_id="teste",
    )

    expected_workspace = (
        create_workspace_path(
            tmp_path,
            project_id="teste",
        )
    )

    assert workspace == expected_workspace
    assert workspace.exists()
    assert workspace.is_dir()


def test_deve_criar_raiz_do_workspace_quando_nao_existir(
    tmp_path: Path,
):
    """
    Deve criar a raiz .work quando ela ainda não existir.
    """

    workspace_root = (
        tmp_path
        / ".work"
    )

    assert not workspace_root.exists()

    service = create_service(
        tmp_path,
    )

    workspace = service.create(
        project_id="teste",
    )

    assert workspace_root.exists()
    assert workspace_root.is_dir()
    assert workspace.exists()
    assert workspace.is_dir()


def test_deve_remover_workspace_anterior_antes_de_criar_novamente(
    tmp_path: Path,
):
    """
    Deve remover resíduos de uma execução anterior
    antes de criar o novo workspace.
    """

    service = create_service(
        tmp_path,
    )

    workspace = service.create(
        project_id="teste",
    )

    arquivo_residual = (
        workspace
        / "residuo.tmp"
    )

    arquivo_residual.write_text(
        "residuo",
        encoding="utf-8",
    )

    assert arquivo_residual.exists()

    novo_workspace = service.create(
        project_id="teste",
    )

    assert novo_workspace == workspace
    assert novo_workspace.exists()
    assert novo_workspace.is_dir()
    assert not arquivo_residual.exists()


def test_deve_permitir_workspaces_de_projetos_diferentes(
    tmp_path: Path,
):
    """
    Deve manter workspaces de projetos diferentes
    independentes entre si.
    """

    service = create_service(
        tmp_path,
    )

    primeiro = service.create(
        project_id="projeto1",
    )

    segundo = service.create(
        project_id="projeto2",
    )

    assert primeiro.exists()
    assert segundo.exists()

    assert primeiro != segundo

    assert primeiro.name == "projeto1"
    assert segundo.name == "projeto2"


def test_deve_remover_workspace_do_projeto(
    tmp_path: Path,
):
    """
    Deve remover o workspace de uma execução.
    """

    service = create_service(
        tmp_path,
    )

    workspace = service.create(
        project_id="teste",
    )

    arquivo = (
        workspace
        / "arquivo.txt"
    )

    arquivo.write_text(
        "teste",
        encoding="utf-8",
    )

    assert workspace.exists()
    assert arquivo.exists()

    service.cleanup(
        workspace_path=workspace,
    )

    assert not workspace.exists()


def test_deve_ignorar_cleanup_de_workspace_inexistente(
    tmp_path: Path,
):
    """
    Não deve falhar quando o workspace já não existir.
    """

    service = create_service(
        tmp_path,
    )

    workspace = (
        create_workspace_path(
            tmp_path,
            project_id="teste",
        )
    )

    assert not workspace.exists()

    service.cleanup(
        workspace_path=workspace,
    )

    assert not workspace.exists()


def test_deve_remover_todos_os_workspaces_da_raiz(
    tmp_path: Path,
):
    """
    Deve remover todos os workspaces existentes na raiz.
    """

    service = create_service(
        tmp_path,
    )

    primeiro = service.create(
        project_id="projeto1",
    )

    segundo = service.create(
        project_id="projeto2",
    )

    (primeiro / "arquivo.txt").write_text(
        "teste",
        encoding="utf-8",
    )

    (segundo / "arquivo.txt").write_text(
        "teste",
        encoding="utf-8",
    )

    workspace_root = (
        tmp_path
        / ".work"
    )

    assert primeiro.exists()
    assert segundo.exists()

    service.cleanup_root()

    assert workspace_root.exists()
    assert workspace_root.is_dir()
    assert list(workspace_root.iterdir()) == []


def test_deve_remover_arquivo_residual_da_raiz(
    tmp_path: Path,
):
    """
    Deve remover arquivos que eventualmente tenham ficado
    diretamente na raiz do workspace.
    """

    workspace_root = (
        tmp_path
        / ".work"
    )

    workspace_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    arquivo_residual = (
        workspace_root
        / "residuo.tmp"
    )

    arquivo_residual.write_text(
        "residuo",
        encoding="utf-8",
    )

    assert arquivo_residual.exists()

    service = create_service(
        tmp_path,
    )

    service.cleanup_root()

    assert workspace_root.exists()
    assert workspace_root.is_dir()
    assert not arquivo_residual.exists()


def test_deve_rejeitar_project_id_vazio(
    tmp_path: Path,
):
    """
    Deve rejeitar ProjectId vazio.
    """

    service = create_service(
        tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="ProjectId não foi informado.",
    ):
        service.create(
            project_id="",
        )


def test_deve_rejeitar_project_id_apenas_com_espacos(
    tmp_path: Path,
):
    """
    Deve rejeitar ProjectId contendo apenas espaços.
    """

    service = create_service(
        tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="ProjectId não foi informado.",
    ):
        service.create(
            project_id="   ",
        )


def test_deve_rejeitar_workspace_root_nulo():
    """
    Deve rejeitar WorkspaceRoot nulo.
    """

    with pytest.raises(
        ValueError,
        match="WorkspaceRoot não foi informado.",
    ):
        AdvancedInstallerWorkspaceService(
            workspace_root=None,
        )


def test_deve_rejeitar_workspace_root_que_seja_arquivo(
    tmp_path: Path,
):
    """
    Deve rejeitar uma raiz que já exista como arquivo.
    """

    workspace_root = (
        tmp_path
        / ".work"
    )

    workspace_root.write_text(
        "arquivo",
        encoding="utf-8",
    )

    service = AdvancedInstallerWorkspaceService(
        workspace_root=workspace_root,
    )

    with pytest.raises(
        ValueError,
        match="O workspace do projeto não é um diretório",
    ):
        service.create(
            project_id="teste",
        )


def test_deve_rejeitar_workspace_path_nulo(
    tmp_path: Path,
):
    """
    Deve rejeitar WorkspacePath nulo.
    """

    service = create_service(
        tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="WorkspacePath não foi informado.",
    ):
        service.cleanup(
            workspace_path=None,
        )


def test_deve_rejeitar_workspace_path_que_seja_arquivo(
    tmp_path: Path,
):
    """
    Deve rejeitar Cleanup quando WorkspacePath for um arquivo.
    """

    workspace_root = (
        tmp_path
        / ".work"
    )

    workspace_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    arquivo = (
        workspace_root
        / "workspace.tmp"
    )

    arquivo.write_text(
        "arquivo",
        encoding="utf-8",
    )

    service = create_service(
        tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="WorkspacePath não é um diretório",
    ):
        service.cleanup(
            workspace_path=arquivo,
        )


def test_deve_rejeitar_workspace_root_que_nao_seja_diretorio_no_cleanup_root(
    tmp_path: Path,
):
    """
    Deve rejeitar CleanupRoot quando a raiz do workspace
    existir como arquivo.
    """

    workspace_root = (
        tmp_path
        / ".work"
    )

    workspace_root.write_text(
        "arquivo",
        encoding="utf-8",
    )

    service = create_service(
        tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="WorkspaceRoot não é um diretório",
    ):
        service.cleanup_root()


def test_deve_criar_estrutura_esperada_para_workspace_do_projeto(
    tmp_path: Path,
):
    """
    Deve permitir a criação da estrutura que será utilizada
    pelo Advanced Installer.

    A criação dos diretórios AIP, Prerequisites e Release
    ainda pertence à etapa de preparação do workspace.
    """

    service = create_service(
        tmp_path,
    )

    workspace = service.create(
        project_id="teste",
    )

    aip_directory = (
        workspace
        / "AIP"
    )

    prerequisites_directory = (
        workspace
        / "Prerequisites"
    )

    release_directory = (
        workspace
        / "Release"
    )

    aip_directory.mkdir()
    prerequisites_directory.mkdir()
    release_directory.mkdir()

    assert aip_directory.exists()
    assert aip_directory.is_dir()

    assert prerequisites_directory.exists()
    assert prerequisites_directory.is_dir()

    assert release_directory.exists()
    assert release_directory.is_dir()

    assert create_workspace_aip_path(
        tmp_path,
        project_id="teste",
    ).parent == aip_directory

    assert create_workspace_prerequisites_path(
        tmp_path,
        project_id="teste",
    ) == prerequisites_directory

    assert create_workspace_publish_path(
        tmp_path,
        project_id="teste",
    ) == release_directory
