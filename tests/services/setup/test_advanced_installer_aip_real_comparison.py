"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_aip_real_comparison.py
Descrição : Diagnóstico real da comparação entre o AIP do
            LinkPagamento e o diretório bin\Release atual.

IMPORTANTE:
    Este teste NÃO altera o AIP.
--------------------------------------------------------------------
"""

from pathlib import Path


from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.services.setup.advanced_installer_aip_file_parser import (
    AdvancedInstallerAipFileParser,
)

from app.services.setup.advanced_installer_aip_file_comparator import (
    AdvancedInstallerAipFileComparator,
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
    Deve analisar o AIP real contra o Release real.

    Nenhum arquivo é alterado.
    """

    #
    # ============================================================
    # 1. Validar ambiente.
    # ============================================================
    #

    assert AIP_PATH.exists(), (
        "AIP não encontrado:\n"
        f"{AIP_PATH}"
    )

    assert PUBLISH_PATH.exists(), (
        "Release não encontrado:\n"
        f"{PUBLISH_PATH}"
    )

    assert PUBLISH_PATH.is_dir(), (
        "Release não é um diretório:\n"
        f"{PUBLISH_PATH}"
    )

    #
    # ============================================================
    # 2. Ler AIP.
    # ============================================================
    #

    content = (
        AIP_PATH.read_text(
            encoding="utf-8",
        )
    )

    #
    # ============================================================
    # 3. Parser.
    # ============================================================
    #

    parser = (
        AdvancedInstallerAipFileParser()
    )

    aip_files = parser.parse(
        content=content,
        publish_path=PUBLISH_PATH,
    )

    assert aip_files, (
        "Nenhum arquivo individual foi encontrado no AIP."
    )

    #
    # ============================================================
    # 4. Comparador.
    # ============================================================
    #

    comparator = (
        AdvancedInstallerAipFileComparator()
    )

    results = comparator.compare(
        aip_files=aip_files,
        publish_path=PUBLISH_PATH,
    )

    assert results

    #
    # ============================================================
    # 5. Separar resultados.
    # ============================================================
    #

    keep_files = [
        result
        for result in results
        if result.action
        == SetupFileAction.KEEP
    ]

    remove_files = [
        result
        for result in results
        if result.action
        == SetupFileAction.REMOVE
    ]

    add_files = [
        result
        for result in results
        if result.action
        == SetupFileAction.ADD
    ]

    #
    # ============================================================
    # 6. Exibir resumo.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] ANÁLISE REAL DO AIP"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] AIP:"
    )

    print(
        AIP_PATH
    )

    print()

    print(
        "[OuroBuild] Release:"
    )

    print(
        PUBLISH_PATH
    )

    print()

    print(
        "[OuroBuild] Arquivos individuais no AIP:"
    )

    print(
        len(aip_files)
    )

    print()

    print(
        "[OuroBuild] KEEP:"
    )

    print(
        len(keep_files)
    )

    print(
        "[OuroBuild] REMOVE:"
    )

    print(
        len(remove_files)
    )

    print(
        "[OuroBuild] ADD:"
    )

    print(
        len(add_files)
    )

    print(
        "=" * 80
    )

    #
    # ============================================================
    # 7. Exibir KEEP.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] KEEP"
    )

    print(
        "=" * 80
    )

    for result in keep_files:

        print(
            f"[KEEP] "
            f"{result.name}"
            f" | "
            f"{result.source_path}"
        )

    #
    # ============================================================
    # 8. Exibir REMOVE.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] REMOVE"
    )

    print(
        "=" * 80
    )

    for result in remove_files:

        print(
            f"[REMOVE] "
            f"{result.name}"
            f" | "
            f"{result.source_path}"
        )

    #
    # ============================================================
    # 9. Exibir ADD.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] ADD"
    )

    print(
        "=" * 80
    )

    for result in add_files:

        print(
            f"[ADD] "
            f"{result.name}"
            f" | "
            f"{result.source_path}"
        )

    #
    # ============================================================
    # 10. Resultado final.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] ANÁLISE CONCLUÍDA"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] O AIP ORIGINAL NÃO FOI ALTERADO."
    )

    print(
        "=" * 80
    )