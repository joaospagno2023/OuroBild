"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : prepare_real_vdproj.py
Descrição : Prepara uma cópia real do .vdproj do OuroNet.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.bootstrap import Bootstrap


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

WORKSPACE_ROOT = Path(
    r"C:\Custom\ourobuild\workspace\real_setup"
)


def main() -> None:
    """
    Prepara uma cópia real do .vdproj.
    """

    print()
    print("=" * 70)
    print("PREPARAÇÃO REAL DO VDPROJ")
    print("=" * 70)

    print()
    print(f"VDPROJ   : {VDPROJ_PATH}")
    print(f"PUBLISH  : {PUBLISH_PATH}")
    print(f"WORKSPACE: {WORKSPACE_ROOT}")

    #
    # Validações
    #

    if not VDPROJ_PATH.exists():
        raise FileNotFoundError(
            f".vdproj não encontrado: {VDPROJ_PATH}"
        )

    if not PUBLISH_PATH.exists():
        raise FileNotFoundError(
            f"Publish não encontrado: {PUBLISH_PATH}"
        )

    #
    # Bootstrap real
    #

    bootstrap = Bootstrap()

    #
    # Preparar cópia
    #

    prepared_project = (
        bootstrap.setup_project_preparer.prepare(
            setup_project_path=VDPROJ_PATH,
            publish_path=PUBLISH_PATH,
            workspace_root=WORKSPACE_ROOT,
            template_file_name=(
                VDPROJ_PATH.name
            ),
        )
    )

    #
    # Resultado
    #

    print()
    print("=" * 70)
    print("PREPARAÇÃO CONCLUÍDA")
    print("=" * 70)

    print()
    print(
        f"Projeto preparado:"
        f"\n{prepared_project}"
    )

    print()
    print(
        f"Existe: "
        f"{prepared_project.exists()}"
    )

    print()
    print(
        f"Tamanho: "
        f"{prepared_project.stat().st_size} bytes"
    )


if __name__ == "__main__":
    main()