"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_workspace_service.py
Descrição : Testes do SetupWorkspaceService.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.services.setup.setup_workspace_service import (
    SetupWorkspaceService,
)


def test_deve_criar_copia_do_setup(tmp_path: Path):
    """
    Deve criar uma cópia independente do .vdproj.
    """

    setup_file = (
        tmp_path
        / "Original.Setup.vdproj"
    )

    setup_file.write_text(
        "conteudo original",
        encoding="utf-8",
    )

    workspace_root = (
        tmp_path
        / "workspace"
    )

    service = (
        SetupWorkspaceService()
    )

    result = service.create_workspace(
        setup_project_path=setup_file,
        workspace_root=workspace_root,
    )

    assert result.exists()

    assert result != setup_file

    assert (
        result.read_text(
            encoding="utf-8",
        )
        == "conteudo original"
    )

    assert (
        setup_file.read_text(
            encoding="utf-8",
        )
        == "conteudo original"
    )


def test_deve_ler_workspace(tmp_path: Path):
    """
    Deve ler o conteúdo do projeto de trabalho.
    """

    setup_file = (
        tmp_path
        / "Setup.vdproj"
    )

    setup_file.write_text(
        "conteudo",
        encoding="utf-8",
    )

    service = (
        SetupWorkspaceService()
    )

    result = service.read(
        workspace_project_path=setup_file,
    )

    assert result == "conteudo"


def test_deve_escrever_workspace(tmp_path: Path):
    """
    Deve escrever no projeto de trabalho.
    """

    setup_file = (
        tmp_path
        / "Setup.vdproj"
    )

    setup_file.write_text(
        "original",
        encoding="utf-8",
    )

    service = (
        SetupWorkspaceService()
    )

    service.write(
        workspace_project_path=setup_file,
        content="alterado",
    )

    assert (
        setup_file.read_text(
            encoding="utf-8",
        )
        == "alterado"
    )


def test_deve_preservar_original_apos_alterar_copia(
    tmp_path: Path,
):
    """
    Deve garantir que alterar a cópia não altera
    o arquivo original.
    """

    setup_file = (
        tmp_path
        / "Setup.vdproj"
    )

    setup_file.write_text(
        "original",
        encoding="utf-8",
    )

    workspace_root = (
        tmp_path
        / "workspace"
    )

    service = (
        SetupWorkspaceService()
    )

    workspace_file = (
        service.create_workspace(
            setup_project_path=setup_file,
            workspace_root=workspace_root,
        )
    )

    service.write(
        workspace_project_path=workspace_file,
        content="alterado",
    )

    assert (
        setup_file.read_text(
            encoding="utf-8",
        )
        == "original"
    )

    assert (
        workspace_file.read_text(
            encoding="utf-8",
        )
        == "alterado"
    )


def test_deve_remover_workspace(
    tmp_path: Path,
):
    """
    Deve remover o workspace temporário.
    """

    workspace_root = (
        tmp_path
        / "workspace"
    )

    workspace_root.mkdir()

    (
        workspace_root
        / "Setup.vdproj"
    ).write_text(
        "teste",
        encoding="utf-8",
    )

    service = (
        SetupWorkspaceService()
    )

    service.cleanup(
        workspace_root=workspace_root,
    )

    assert not workspace_root.exists()


def test_deve_rejeitar_setup_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar um Setup que não existe.
    """

    service = (
        SetupWorkspaceService()
    )

    with pytest.raises(
        FileNotFoundError,
    ):
        service.create_workspace(
            setup_project_path=(
                tmp_path
                / "nao_existe.vdproj"
            ),
            workspace_root=(
                tmp_path
                / "workspace"
            ),
        )


def test_deve_rejeitar_workspace_none():
    """
    Deve rejeitar WorkspaceRoot não informado.
    """

    service = (
        SetupWorkspaceService()
    )

    with pytest.raises(
        ValueError,
        match="WorkspaceRoot não foi informado.",
    ):
        service.create_workspace(
            setup_project_path=Path(
                "Setup.vdproj"
            ),
            workspace_root=None,
        )