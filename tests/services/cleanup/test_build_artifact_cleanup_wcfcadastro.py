"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_build_artifact_cleanup_wcfcadastro.py
Descrição : Valida a limpeza específica do WCF Cadastro.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.services.cleanup.build_artifact_cleanup_service import (
    BuildArtifactCleanupService,
)

from app.services.cleanup.cleanup_rules_provider import (
    CleanupRulesProvider,
)


def test_wcfcadastro_remove_diretorios_nativos(
    tmp_path: Path,
) -> None:
    """
    O WCF Cadastro deve remover os diretórios
    x86, x64 e arm64 do bin.

    As DLLs existentes diretamente em bin devem
    permanecer.
    """

    release = (
        tmp_path
        / "Release"
    )

    bin_path = (
        release
        / "bin"
    )

    bin_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    #
    # DLL que deve permanecer diretamente em bin.
    #

    root_dll = (
        bin_path
        / "OuroNet.Server.WCF.Cadastre.dll"
    )

    root_dll.write_text(
        "dll",
        encoding="utf-8",
    )

    #
    # Diretórios nativos que devem ser removidos.
    #

    native_directories = [
        "x86",
        "x64",
        "arm64",
    ]

    for directory_name in native_directories:

        directory = (
            bin_path
            / directory_name
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        (
            directory
            / "Native.dll"
        ).write_text(
            "dll",
            encoding="utf-8",
        )

    #
    # Obtém as regras reais do projeto.
    #

    rules = (
        CleanupRulesProvider.get_rules(
            project_id="wcfcadastro",
        )
    )

    service = (
        BuildArtifactCleanupService(
            rules=rules,
        )
    )

    #
    # Executa o Cleanup.
    #

    result = (
        service.execute(
            workspace_path=release,
            project_id="wcfcadastro",
        )
    )

    #
    # Os diretórios nativos devem ter sido removidos.
    #

    for directory_name in native_directories:

        assert not (
            bin_path
            / directory_name
        ).exists()

    #
    # A DLL da raiz deve permanecer.
    #

    assert root_dll.exists()

    #
    # Não pode ter ocorrido erro.
    #

    assert result.errors == []