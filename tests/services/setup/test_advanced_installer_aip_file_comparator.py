"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_aip_file_comparator.py
Descrição : Testes do comparador de arquivos do Advanced Installer.
--------------------------------------------------------------------
"""

from pathlib import Path


from app.models.setup.setup_file import (
    SetupFile,
)

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.services.setup.advanced_installer_aip_file_comparator import (
    AdvancedInstallerAipFileComparator,
)


def test_deve_manter_arquivo_existente_no_release(
    tmp_path: Path,
):
    """
    Arquivo existente no AIP e no Release deve ser KEEP.
    """

    release = (
        tmp_path
        / "Release"
    )

    release.mkdir()

    file_path = (
        release
        / "Teste.exe"
    )

    file_path.write_text(
        "teste",
        encoding="utf-8",
    )

    aip_files = [
        SetupFile(
            name="Teste.exe",
            source_path="Teste.exe",
            publish_path=file_path,
        )
    ]

    comparator = (
        AdvancedInstallerAipFileComparator()
    )

    results = comparator.compare(
        aip_files=aip_files,
        publish_path=release,
    )

    assert len(results) == 1

    assert (
        results[0].action
        == SetupFileAction.KEEP
    )

    assert (
        results[0].name
        == "Teste.exe"
    )

    assert (
        results[0].source_path
        == "Teste.exe"
    )

    assert (
        results[0].publish_path
        == file_path
    )


def test_deve_remover_arquivo_que_nao_existe_no_release(
    tmp_path: Path,
):
    """
    Arquivo existente no AIP mas ausente no Release
    deve ser REMOVE.
    """

    release = (
        tmp_path
        / "Release"
    )

    release.mkdir()

    old_file = SetupFile(
        name="ArquivoAntigo.dll",
        source_path="ArquivoAntigo.dll",
        publish_path=(
            release
            / "ArquivoAntigo.dll"
        ),
    )

    comparator = (
        AdvancedInstallerAipFileComparator()
    )

    results = comparator.compare(
        aip_files=[
            old_file,
        ],
        publish_path=release,
    )

    assert len(results) == 1

    assert (
        results[0].action
        == SetupFileAction.REMOVE
    )

    assert (
        results[0].name
        == "ArquivoAntigo.dll"
    )

    assert (
        results[0].source_path
        == "ArquivoAntigo.dll"
    )


def test_deve_adicionar_arquivo_novo_do_release(
    tmp_path: Path,
):
    """
    Arquivo existente no Release mas ausente no AIP
    deve ser ADD.
    """

    release = (
        tmp_path
        / "Release"
    )

    release.mkdir()

    new_file = (
        release
        / "Novo.dll"
    )

    new_file.write_text(
        "novo",
        encoding="utf-8",
    )

    comparator = (
        AdvancedInstallerAipFileComparator()
    )

    results = comparator.compare(
        aip_files=[],
        publish_path=release,
    )

    assert len(results) == 1

    assert (
        results[0].action
        == SetupFileAction.ADD
    )

    assert (
        results[0].name
        == "Novo.dll"
    )

    assert (
        results[0].source_path
        == "Novo.dll"
    )

    assert (
        results[0].publish_path
        == new_file
    )


def test_deve_comparar_sem_diferenciar_maiusculas(
    tmp_path: Path,
):
    """
    A comparação deve ser case-insensitive.
    """

    release = (
        tmp_path
        / "Release"
    )

    release.mkdir()

    file_path = (
        release
        / "Teste.DLL"
    )

    file_path.write_text(
        "teste",
        encoding="utf-8",
    )

    aip_files = [
        SetupFile(
            name="teste.dll",
            source_path="teste.dll",
            publish_path=(
                release
                / "teste.dll"
            ),
        )
    ]

    comparator = (
        AdvancedInstallerAipFileComparator()
    )

    results = comparator.compare(
        aip_files=aip_files,
        publish_path=release,
    )

    assert len(results) == 1

    assert (
        results[0].action
        == SetupFileAction.KEEP
    )

    assert (
        results[0].name
        == "teste.dll"
    )


def test_deve_comparar_subdiretorios(
    tmp_path: Path,
):
    """
    Arquivos em subdiretórios devem ser comparados
    utilizando o caminho relativo.
    """

    release = (
        tmp_path
        / "Release"
    )

    native_directory = (
        release
        / "x64"
    )

    native_directory.mkdir(
        parents=True,
    )

    file_path = (
        native_directory
        / "Native.dll"
    )

    file_path.write_text(
        "native",
        encoding="utf-8",
    )

    aip_files = [
        SetupFile(
            name="Native.dll",
            source_path=r"x64\Native.dll",
            publish_path=file_path,
        )
    ]

    comparator = (
        AdvancedInstallerAipFileComparator()
    )

    results = comparator.compare(
        aip_files=aip_files,
        publish_path=release,
    )

    assert len(results) == 1

    assert (
        results[0].action
        == SetupFileAction.KEEP
    )

    assert (
        results[0].name
        == "Native.dll"
    )


def test_deve_identificar_keep_remove_e_add(
    tmp_path: Path,
):
    """
    Deve identificar simultaneamente:

        KEEP
        REMOVE
        ADD
    """

    release = (
        tmp_path
        / "Release"
    )

    release.mkdir()

    keep_file = (
        release
        / "Keep.dll"
    )

    add_file = (
        release
        / "Add.dll"
    )

    keep_file.write_text(
        "keep",
        encoding="utf-8",
    )

    add_file.write_text(
        "add",
        encoding="utf-8",
    )

    aip_files = [
        SetupFile(
            name="Keep.dll",
            source_path="Keep.dll",
            publish_path=keep_file,
        ),
        SetupFile(
            name="Remove.dll",
            source_path="Remove.dll",
            publish_path=(
                release
                / "Remove.dll"
            ),
        ),
    ]

    comparator = (
        AdvancedInstallerAipFileComparator()
    )

    results = comparator.compare(
        aip_files=aip_files,
        publish_path=release,
    )

    assert len(results) == 3

    actions = {
        result.name: result.action
        for result in results
    }

    assert (
        actions["Keep.dll"]
        == SetupFileAction.KEEP
    )

    assert (
        actions["Remove.dll"]
        == SetupFileAction.REMOVE
    )

    assert (
        actions["Add.dll"]
        == SetupFileAction.ADD
    )