"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_build_artifact_cleanup_linkpagamento.py
Descrição : Teste das regras de limpeza do LinkPagamento.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.services.cleanup.build_artifact_cleanup_service import (
    BuildArtifactCleanupService,
)

from app.services.cleanup.cleanup_rules_provider import (
    CleanupRulesProvider,
)


def test_deve_aplicar_regras_de_limpeza_do_linkpagamento(
    tmp_path: Path,
):
    """
    Deve aplicar as regras globais e específicas do
    projeto LinkPagamento.

    Regra global de arquivos:

        * -> REMOVE

    Regra global de diretórios:

        * -> REMOVE

    Regra específica:

        OuroNetWinServiceLinkPagamento.exe.config
            -> PRESERVE
    """

    #
    # ============================================================
    # 1. Criar estrutura de publicação.
    # ============================================================
    #

    release = (
        tmp_path
        / "Release"
    )

    release.mkdir()

    #
    # Arquivo normal.
    #

    dll_file = (
        release
        / "OuroNet.dll"
    )

    dll_file.write_text(
        "dll",
        encoding="utf-8",
    )

    #
    # PDB.
    #

    pdb_file = (
        release
        / "OuroNet.pdb"
    )

    pdb_file.write_text(
        "pdb",
        encoding="utf-8",
    )

    #
    # XML.
    #

    xml_file = (
        release
        / "OuroNet.xml"
    )

    xml_file.write_text(
        "xml",
        encoding="utf-8",
    )

    #
    # Configuração que não é a exceção do projeto.
    #

    config_file = (
        release
        / "OutroServico.exe.config"
    )

    config_file.write_text(
        "config",
        encoding="utf-8",
    )

    #
    # Configuração específica do LinkPagamento.
    #

    linkpagamento_config = (
        release
        / "OuroNetWinServiceLinkPagamento.exe.config"
    )

    linkpagamento_config.write_text(
        "config",
        encoding="utf-8",
    )

    #
    # DLL contendo "Config" no nome.
    #
    # A regra global atual é:
    #
    #     * -> REMOVE
    #
    # Portanto ela deve ser removida.
    #

    config_dll = (
        release
        / "MeuConfig.dll"
    )

    config_dll.write_text(
        "dll",
        encoding="utf-8",
    )

    #
    # Diretório de logs.
    #

    log_directory = (
        release
        / "log"
    )

    log_directory.mkdir()

    log_file = (
        log_directory
        / "arquivo.log"
    )

    log_file.write_text(
        "log",
        encoding="utf-8",
    )

    #
    # Diretório normal.
    #

    x64_directory = (
        release
        / "x64"
    )

    x64_directory.mkdir()

    x64_file = (
        x64_directory
        / "Native.dll"
    )

    x64_file.write_text(
        "dll",
        encoding="utf-8",
    )

    #
    # ============================================================
    # 2. Obter regras do projeto.
    # ============================================================
    #

    rules = (
        CleanupRulesProvider.get_rules(
            project_id="linkpagamento",
        )
    )

    #
    # ============================================================
    # 3. Criar serviço.
    # ============================================================
    #

    service = (
        BuildArtifactCleanupService(
            rules=rules,
        )
    )

    #
    # ============================================================
    # 4. Executar limpeza.
    # ============================================================
    #

    result = (
        service.execute(
            workspace_path=release,
            project_id="linkpagamento",
        )
    )

    #
    # ============================================================
    # 5. Arquivos que devem ser removidos.
    # ============================================================
    #

    assert not pdb_file.exists()

    assert not xml_file.exists()

    assert not config_file.exists()

    assert config_dll.exists()

    #
    # ============================================================
    # 6. Configuração específica deve ser preservada.
    # ============================================================
    #

    assert (
        linkpagamento_config.exists()
    )

    #
    # ============================================================
    # 7. Diretório log deve ser removido.
    # ============================================================
    #

    assert not log_directory.exists()

    #
    # ============================================================
    # 8. Diretório normal também deve ser removido.
    #
    # A regra global determina que todos os diretórios
    # do Release sejam removidos.
    # ============================================================
    #

    assert not x64_directory.exists()

    assert not x64_file.exists()

    #
    # ============================================================
    # 9. Arquivo normal também deve ser removido.
    #
    # A política atual é:
    #
    #     FILE "*" -> REMOVE
    #
    # Portanto, nenhum arquivo comum permanece no Release.
    # ============================================================
    #

    assert not dll_file.exists()

    #
    # ============================================================
    # 10. Resultado deve indicar sucesso.
    # ============================================================
    #

    assert result.success

    #
    # ============================================================
    # 11. Diagnóstico.
    # ============================================================
    #

    print()

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] CLEANUP LINKPAGAMENTO"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] PDB removido: OK"
    )

    print(
        "[OuroBuild] XML removido: OK"
    )

    print(
        "[OuroBuild] CONFIG removido: OK"
    )

    print(
        "[OuroBuild] CONFIG do LinkPagamento preservado: OK"
    )

    print(
        "[OuroBuild] MeuConfig.dll removido: OK"
    )

    print(
        "[OuroBuild] LOG removido: OK"
    )

    print(
        "[OuroBuild] x64 removido: OK"
    )

    print(
        "[OuroBuild] Arquivo normal removido: OK"
    )

    print(
        "=" * 80
    )