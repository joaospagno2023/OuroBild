"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_aip_file_integration.py
Descrição : Teste de integração entre Parser e Comparator
            utilizando o AIP real do LinkPagamento e o Release real.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.services.setup.advanced_installer_aip_file_comparator import (
    AdvancedInstallerAipFileComparator,
)

from app.services.setup.advanced_installer_aip_file_parser import (
    AdvancedInstallerAipFileParser,
)


AIP_ROOT = Path(
    r"C:\DvpLocal\WorkSpaceTFS"
    r"\Transferencia de Arquivo"
    r"\TransferenciaDeArquivos"
    r"\Setups"
    r"\Installers"
    r"\Projects"
)


AIP_PATH = (
    AIP_ROOT
    / "OuroNet.WinServiceLinkPagamento.aip"
)


PUBLISH_PATH = Path(
    r"C:\DvpLocal\WorkSpaceTFS"
    r"\OuroNet"
    r"\Scc"
    r"\Producao"
    r"\OuroNet"
    r"\02-Source"
    r"\01-Client"
    r"\OuroNet.Client.WinService.LinkPagamento"
    r"\bin"
    r"\Release"
)


def test_deve_comparar_aip_real_com_release_real():
    """
    Deve analisar o AIP real e comparar seus arquivos
    individuais com o Release real.

    Este teste NÃO altera o AIP.
    """

    #
    # ============================================================
    # 1. Validar AIP.
    # ============================================================
    #

    if not AIP_PATH.exists():

        raise FileNotFoundError(
            "AIP do LinkPagamento não encontrado:\n"
            f"{AIP_PATH}"
        )

    if not AIP_PATH.is_file():

        raise ValueError(
            "O AIP do LinkPagamento não é um arquivo:\n"
            f"{AIP_PATH}"
        )

    #
    # ============================================================
    # 2. Validar Release.
    # ============================================================
    #

    if not PUBLISH_PATH.exists():

        raise FileNotFoundError(
            "Pasta Release do LinkPagamento não encontrada:\n"
            f"{PUBLISH_PATH}"
        )

    if not PUBLISH_PATH.is_dir():

        raise ValueError(
            "A pasta Release do LinkPagamento "
            "não é um diretório:\n"
            f"{PUBLISH_PATH}"
        )

    #
    # ============================================================
    # 3. Ler AIP.
    # ============================================================
    #

    content = (
        AIP_PATH.read_text(
            encoding="utf-8",
        )
    )

    #
    # ============================================================
    # 4. Executar Parser.
    # ============================================================
    #

    parser = (
        AdvancedInstallerAipFileParser()
    )

    aip_files = (
        parser.parse(
            content=content,
            publish_path=PUBLISH_PATH,
        )
    )

    #
    # ============================================================
    # 5. Executar Comparator.
    # ============================================================
    #

    comparator = (
        AdvancedInstallerAipFileComparator()
    )

    results = (
        comparator.compare(
            aip_files=aip_files,
            publish_path=PUBLISH_PATH,
        )
    )

    #
    # ============================================================
    # 6. Separar ações.
    # ============================================================
    #

    keep_files = [
        result
        for result in results
        if result.action
        == SetupFileAction.KEEP
    ]

    add_files = [
        result
        for result in results
        if result.action
        == SetupFileAction.ADD
    ]

    remove_files = [
        result
        for result in results
        if result.action
        == SetupFileAction.REMOVE
    ]

    #
    # ============================================================
    # 7. Diagnóstico.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] ANÁLISE DO AIP REAL"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] AIP:"
    )

    print(
        f"[OuroBuild] {AIP_PATH}"
    )

    print()
    print(
        "[OuroBuild] RELEASE:"
    )

    print(
        f"[OuroBuild] {PUBLISH_PATH}"
    )

    print()
    print(
        "[OuroBuild] ARQUIVOS ENCONTRADOS NO AIP:"
    )

    print(
        f"[OuroBuild] {len(aip_files)}"
    )

    print()
    print(
        "[OuroBuild] KEEP:"
    )

    print(
        f"[OuroBuild] {len(keep_files)}"
    )

    print()
    print(
        "[OuroBuild] ADD:"
    )

    print(
        f"[OuroBuild] {len(add_files)}"
    )

    print()
    print(
        "[OuroBuild] REMOVE:"
    )

    print(
        f"[OuroBuild] {len(remove_files)}"
    )

    #
    # ============================================================
    # 8. Mostrar ADD.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] ARQUIVOS ADD"
    )

    print(
        "=" * 80
    )

    for item in add_files:

        print(
            f"[ADD] "
            f"{item.source_path}"
        )

    #
    # ============================================================
    # 9. Mostrar REMOVE.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] ARQUIVOS REMOVE"
    )

    print(
        "=" * 80
    )

    for item in remove_files:

        print(
            f"[REMOVE] "
            f"{item.source_path}"
        )

    #
    # ============================================================
    # 10. Mostrar alguns KEEP.
    #
    # Não precisamos imprimir centenas de arquivos.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] PRIMEIROS KEEP"
    )

    print(
        "=" * 80
    )

    for item in keep_files[:20]:

        print(
            f"[KEEP] "
            f"{item.source_path}"
        )

    if len(keep_files) > 20:

        print(
            "[OuroBuild] "
            f"... mais {len(keep_files) - 20} arquivos."
        )

    #
    # ============================================================
    # 11. Validações básicas.
    # ============================================================
    #

    assert isinstance(
        aip_files,
        list,
    )

    assert isinstance(
        results,
        list,
    )

    #
    # ============================================================
    # 12. Diagnóstico final.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] COMPARAÇÃO CONCLUÍDA"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] Nenhum arquivo foi alterado."
    )

    print(
        "[OuroBuild] Nenhum AIP foi alterado."
    )

    print(
        "=" * 80
    )