"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_file_synchronizer.py
Descrição : Testes do SetupFileSynchronizer.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.setup.setup_file import (
    SetupFile,
)

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.services.setup.setup_file_synchronizer import (
    SetupFileSynchronizer,
)


def create_setup_file(
    name: str,
    publish_path: Path,
) -> SetupFile:
    """
    Cria um SetupFile para teste.
    """

    return SetupFile(
        name=name,
        source_path=name,
        publish_path=(
            publish_path / name
        ),
    )


def test_deve_identificar_arquivo_para_atualizacao(
    tmp_path: Path,
):
    """
    Deve identificar DLL existente no Setup
    e também no publish_path.
    """

    dll = (
        tmp_path
        / "Custom.Framework.dll"
    )

    dll.write_text(
        "DLL",
        encoding="utf-8",
    )

    setup_file = create_setup_file(
        "Custom.Framework.dll",
        tmp_path,
    )

    synchronizer = (
        SetupFileSynchronizer()
    )

    result = synchronizer.synchronize(
        setup_files=[
            setup_file,
        ],
        publish_path=tmp_path,
    )

    assert len(result) == 1

    assert result[0].action == (
        SetupFileAction.UPDATE
    )


def test_deve_identificar_arquivo_para_remocao(
    tmp_path: Path,
):
    """
    Deve identificar DLL existente no Setup,
    mas ausente no publish_path.
    """

    setup_file = create_setup_file(
        "Antiga.dll",
        tmp_path,
    )

    synchronizer = (
        SetupFileSynchronizer()
    )

    result = synchronizer.synchronize(
        setup_files=[
            setup_file,
        ],
        publish_path=tmp_path,
    )

    assert len(result) == 1

    assert result[0].action == (
        SetupFileAction.REMOVE
    )


def test_deve_identificar_arquivo_novo(
    tmp_path: Path,
):
    """
    Deve identificar DLL existente no publish_path,
    mas ausente no Setup.
    """

    dll = (
        tmp_path
        / "Nova.dll"
    )

    dll.write_text(
        "DLL",
        encoding="utf-8",
    )

    synchronizer = (
        SetupFileSynchronizer()
    )

    result = synchronizer.synchronize(
        setup_files=[],
        publish_path=tmp_path,
    )

    assert len(result) == 1

    assert result[0].name == (
        "Nova.dll"
    )

    assert result[0].action == (
        SetupFileAction.ADD
    )


def test_deve_identificar_adicao_e_remocao(
    tmp_path: Path,
):
    """
    Deve identificar simultaneamente uma DLL
    nova e uma DLL removida.
    """

    nova = (
        tmp_path
        / "Nova.dll"
    )

    nova.write_text(
        "DLL",
        encoding="utf-8",
    )

    setup_file = create_setup_file(
        "Antiga.dll",
        tmp_path,
    )

    synchronizer = (
        SetupFileSynchronizer()
    )

    result = synchronizer.synchronize(
        setup_files=[
            setup_file,
        ],
        publish_path=tmp_path,
    )

    actions = {
        item.name: item.action
        for item in result
    }

    assert actions[
        "Antiga.dll"
    ] == SetupFileAction.REMOVE

    assert actions[
        "Nova.dll"
    ] == SetupFileAction.ADD