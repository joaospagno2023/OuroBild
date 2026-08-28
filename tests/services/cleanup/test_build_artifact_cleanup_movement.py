"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_build_artifact_cleanup_movement.py
Descrição : Testes das regras de limpeza do Movement.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.services.cleanup.build_artifact_cleanup_service import (
    BuildArtifactCleanupService,
)

from app.services.cleanup.cleanup_rules_provider import (
    CleanupRulesProvider,
)


def test_deve_preservar_pasta_xml_do_movement(
    tmp_path: Path,
):
    """
    Deve remover os diretórios do bin do Movement,
    exceto a pasta Xml.

    Regra global:

        DIRECTORY * -> REMOVE

    Regra específica do Movement:

        DIRECTORY Xml -> PRESERVE
    """

    #
    # ============================================================
    # 1. Criar estrutura real do bin.
    # ============================================================
    #

    bin_path = (
        tmp_path
        / "bin"
    )

    bin_path.mkdir()

    #
    # ============================================================
    # 2. Criar diretórios que devem ser removidos.
    # ============================================================
    #

    x64_directory = (
        bin_path
        / "x64"
    )

    x64_directory.mkdir()

    (
        x64_directory
        / "Native.dll"
    ).write_text(
        "dll",
        encoding="utf-8",
    )

    x86_directory = (
        bin_path
        / "x86"
    )

    x86_directory.mkdir()

    (
        x86_directory
        / "Native.dll"
    ).write_text(
        "dll",
        encoding="utf-8",
    )

    log_directory = (
        bin_path
        / "log"
    )

    log_directory.mkdir()

    (
        log_directory
        / "arquivo.log"
    ).write_text(
        "log",
        encoding="utf-8",
    )

    #
    # ============================================================
    # 3. Criar pasta Xml que deve ser preservada.
    # ============================================================
    #

    xml_directory = (
        bin_path
        / "Xml"
    )

    xml_directory.mkdir()

    xml_file = (
        xml_directory
        / "arquivo.xml"
    )

    xml_file.write_text(
        "<xml />",
        encoding="utf-8",
    )

    xsd_file = (
        xml_directory
        / "schema.xsd"
    )

    xsd_file.write_text(
        "<schema />",
        encoding="utf-8",
    )

    #
    # ============================================================
    # 4. Criar subdiretório dentro de Xml.
    # ============================================================
    #

    xml_subdirectory = (
        xml_directory
        / "Movimento"
    )

    xml_subdirectory.mkdir()

    nested_xml_file = (
        xml_subdirectory
        / "movimento.xml"
    )

    nested_xml_file.write_text(
        "<movimento />",
        encoding="utf-8",
    )

    #
    # ============================================================
    # 5. Obter regras do Movement.
    # ============================================================
    #

    rules = (
        CleanupRulesProvider.get_rules(
            project_id="movement",
        )
    )

    #
    # ============================================================
    # 6. Criar serviço.
    # ============================================================
    #

    service = (
        BuildArtifactCleanupService(
            rules=rules,
        )
    )

    #
    # ============================================================
    # 7. Executar Cleanup.
    # ============================================================
    #

    result = (
        service.execute(
            workspace_path=bin_path,
            project_id="movement",
        )
    )

    #
    # ============================================================
    # 8. Diretórios não necessários devem ser removidos.
    # ============================================================
    #

    assert not x64_directory.exists()

    assert not x86_directory.exists()

    assert not log_directory.exists()

    #
    # ============================================================
    # 9. Pasta Xml deve permanecer.
    # ============================================================
    #

    assert xml_directory.exists()

    #
    # ============================================================
    # 10. Arquivos dentro de Xml devem permanecer.
    # ============================================================
    #

    assert xml_file.exists()

    assert xsd_file.exists()

    #
    # ============================================================
    # 11. Subdiretórios de Xml devem permanecer.
    # ============================================================
    #

    assert xml_subdirectory.exists()

    assert nested_xml_file.exists()

    #
    # ============================================================
    # 12. Resultado deve indicar sucesso.
    # ============================================================
    #

    assert result.success

    #
    # ============================================================
    # 13. Diagnóstico.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] CLEANUP MOVIMENT"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] bin/x64 removido: OK"
    )

    print(
        "[OuroBuild] bin/x86 removido: OK"
    )

    print(
        "[OuroBuild] bin/log removido: OK"
    )

    print(
        "[OuroBuild] bin/Xml preservado: OK"
    )

    print(
        "[OuroBuild] Conteúdo de Xml preservado: OK"
    )

    print(
        "[OuroBuild] Subdiretórios de Xml preservados: OK"
    )

    print(
        "=" * 80
    )