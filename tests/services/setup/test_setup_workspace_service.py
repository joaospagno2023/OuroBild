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
    Deve criar uma cópia do arquivo .vdproj.
    """

    original = (
        tmp_path
        / "original"
        / "MeuSetup.vdproj"
    )

    output = (
        tmp_path
        / "workspace"
    )

    original.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    original.write_text(
        "CONTEUDO ORIGINAL",
        encoding="utf-8",
    )

    service = SetupWorkspaceService()

    working_setup = service.create(
        setup_project_path=original,
        setup_output_path=output,
    )

    assert working_setup.exists()

    assert working_setup == (
        output / "MeuSetup.vdproj"
    )

    assert (
        working_setup.read_text(
            encoding="utf-8"
        )
        == "CONTEUDO ORIGINAL"
    )

    assert (
        original.read_text(
            encoding="utf-8"
        )
        == "CONTEUDO ORIGINAL"
    )


def test_deve_criar_diretorio_de_trabalho(
    tmp_path: Path,
):
    """
    Deve criar o diretório de trabalho
    quando ele não existir.
    """

    original = (
        tmp_path
        / "MeuSetup.vdproj"
    )

    output = (
        tmp_path
        / "workspace"
        / "setup"
    )

    original.write_text(
        "SETUP",
        encoding="utf-8",
    )

    service = SetupWorkspaceService()

    working_setup = service.create(
        setup_project_path=original,
        setup_output_path=output,
    )

    assert output.exists()
    assert working_setup.exists()


def test_deve_falhar_quando_setup_nao_existir(
    tmp_path: Path,
):
    """
    Deve falhar quando o .vdproj original
    não existir.
    """

    original = (
        tmp_path
        / "NaoExiste.vdproj"
    )

    output = (
        tmp_path
        / "workspace"
    )

    service = SetupWorkspaceService()

    with pytest.raises(
        FileNotFoundError,
        match="Projeto de Setup não encontrado",
    ):
        service.create(
            setup_project_path=original,
            setup_output_path=output,
        )


def test_nao_deve_alterar_setup_original(
    tmp_path: Path,
):
    """
    Deve preservar o conteúdo do Setup original.
    """

    original = (
        tmp_path
        / "MeuSetup.vdproj"
    )

    output = (
        tmp_path
        / "workspace"
    )

    conteudo = """
"ProductName" = "8:Meu Produto"
"Version" = "8:10.4.8"
"""

    original.write_text(
        conteudo,
        encoding="utf-8",
    )

    service = SetupWorkspaceService()

    working_setup = service.create(
        setup_project_path=original,
        setup_output_path=output,
    )

    working_setup.write_text(
        conteudo.replace(
            "10.4.8",
            "10.4.9",
        ),
        encoding="utf-8",
    )

    assert (
        original.read_text(
            encoding="utf-8"
        )
        == conteudo
    )