"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : inspect_real_vdproj.py
Descrição : Inspeciona o .vdproj real e calcula as alterações
            necessárias em relação ao publish.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.services.setup.setup_file_synchronizer import (
    SetupFileSynchronizer,
)

from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)

from app.services.setup.vdproj_setup_file_loader import (
    VdprojSetupFileLoader,
)

from app.models.setup.setup_file_action import (
    SetupFileAction,
)


VDPROJ_PATH = Path(
    r"C:\DvpLocal\WorkSpaceTFS\OuroNet\Scc\Producao\OuroNet"
    r"\04-Setup\OuroNet.Client.WinServiceLinkPagamento.Setup"
    r"\OuroNet.Client.WinServiceLinkPagamento.Setup.vdproj"
)

PUBLISH_PATH = Path(
    r"C:\DvpLocal\WorkSpaceTFS\OuroNet\Scc\Producao\OuroNet"
    r"\02-Source\01-Client\OuroNet.Client.WinService.LinkPagamento"
    r"\bin\Release"
)


def main() -> None:
    """
    Executa a inspeção do .vdproj real.
    """

    print()
    print("=" * 70)
    print("INSPEÇÃO DO VDPROJ REAL")
    print("=" * 70)

    print()
    print(f"VDPROJ   : {VDPROJ_PATH}")
    print(f"PUBLISH  : {PUBLISH_PATH}")

    print()
    print(
        f"VDPROJ existe : "
        f"{VDPROJ_PATH.exists()}"
    )

    print(
        f"PUBLISH existe: "
        f"{PUBLISH_PATH.exists()}"
    )

    if not VDPROJ_PATH.exists():
        raise FileNotFoundError(
            f".vdproj não encontrado: "
            f"{VDPROJ_PATH}"
        )

    if not PUBLISH_PATH.exists():
        raise FileNotFoundError(
            f"Publish não encontrado: "
            f"{PUBLISH_PATH}"
        )

    #
    # 1. Parser
    #

    parser = VdprojBlockParser()

    #
    # 2. Loader
    #

    loader = VdprojSetupFileLoader(
        parser=parser,
    )

    #
    # 3. Carregar arquivos do Setup
    #

    setup_files = loader.load(
        setup_project_path=VDPROJ_PATH,
        publish_path=PUBLISH_PATH,
    )

    print()
    print("=" * 70)
    print(
        "ARQUIVOS ENCONTRADOS NO VDPROJ: "
        f"{len(setup_files)}"
    )
    print("=" * 70)

    #
    # 4. Synchronizer
    #

    synchronizer = (
        SetupFileSynchronizer()
    )

    changes = synchronizer.synchronize(
        setup_files=setup_files,
        publish_path=PUBLISH_PATH,
    )

    #
    # 5. Separar por ação
    #

    updates = [
    item
    for item in changes
    if item.action == SetupFileAction.UPDATE
    ]

    removes = [
        item
        for item in changes
        if item.action == SetupFileAction.REMOVE
    ]

    adds = [
        item
        for item in changes
        if item.action == SetupFileAction.ADD
    ]

    #
    # 6. Resumo
    #

    print()
    print("=" * 70)
    print("RESUMO DAS ALTERAÇÕES")
    print("=" * 70)

    print()
    print(
        f"UPDATE: {len(updates)}"
    )

    print(
        f"REMOVE: {len(removes)}"
    )

    print(
        f"ADD:    {len(adds)}"
    )

    print(
        f"TOTAL:  {len(changes)}"
    )

    #
    # 7. UPDATE
    #

    print()
    print("=" * 70)
    print("UPDATE")
    print("=" * 70)

    for item in updates:
        print(
            f"  {item.name}"
        )

    #
    # 8. REMOVE
    #

    print()
    print("=" * 70)
    print("REMOVE")
    print("=" * 70)

    for item in removes:
        print(
            f"  {item.name}"
        )

    #
    # 9. ADD
    #

    print()
    print("=" * 70)
    print("ADD")
    print("=" * 70)

    for item in adds:
        print(
            f"  {item.name}"
        )

    #
    # 10. Finalização
    #

    print()
    print("=" * 70)
    print("INSPEÇÃO CONCLUÍDA")
    print("=" * 70)

    print()
    print(
        "Nenhum arquivo foi alterado."
    )


if __name__ == "__main__":
    main()