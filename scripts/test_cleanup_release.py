"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_cleanup_release.py
Descrição : Executa Dry Run do Cleanup em uma cópia do Release.
--------------------------------------------------------------------
"""

import sys

from pathlib import Path


#
# ============================================================
# 1. Localiza a raiz do OuroBuild.
# ============================================================
#

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


#
# ============================================================
# 2. Adiciona a raiz ao sys.path.
# ============================================================
#

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.services.cleanup.build_artifact_cleanup_factory import (
    BuildArtifactCleanupFactory,
)


#
# ============================================================
# 3. Release de teste.
#
# IMPORTANTE:
# O Release original NÃO será alterado.
# ============================================================
#

RELEASE_PATH = Path(
    r"C:\DvpLocal\WorkSpaceTFS\OuroNet\Scc\Producao\OuroNet"
    r"\02-Source\01-Client"
    r"\OuroNet.Client.WinService.LinkPagamento"
    r"\bin\Release.OuroBuild.Teste"
)


PROJECT_ID = "linkpagamento"


def main() -> None:
    """
    Executa o diagnóstico do Cleanup em modo Dry Run.
    """

    print()
    print("=" * 80)
    print("[OuroBuild] CLEANUP DRY RUN - RELEASE DE TESTE")
    print("=" * 80)

    print(
        "[OuroBuild] Projeto:"
    )

    print(
        f"[OuroBuild] {PROJECT_ID}"
    )

    print(
        "[OuroBuild] Release:"
    )

    print(
        f"[OuroBuild] {RELEASE_PATH}"
    )

    print("=" * 80)

    #
    # ========================================================
    # Validação do caminho.
    # ========================================================
    #

    if not RELEASE_PATH.exists():

        raise FileNotFoundError(
            "A pasta Release de teste não existe:\n"
            f"{RELEASE_PATH}"
        )

    if not RELEASE_PATH.is_dir():

        raise ValueError(
            "O caminho informado não é um diretório:\n"
            f"{RELEASE_PATH}"
        )

    #
    # ========================================================
    # Cria o serviço com as regras oficiais.
    # ========================================================
    #

    service = (
        BuildArtifactCleanupFactory.create(
            project_id=PROJECT_ID,
        )
    )

    #
    # ========================================================
    # Executa em DRY RUN.
    #
    # Nenhum arquivo ou diretório será removido.
    # ========================================================
    #

    result = service.execute(
        workspace_path=RELEASE_PATH,
        project_id=PROJECT_ID,
        dry_run=False,
    )

    #
    # ========================================================
    # Resultado.
    # ========================================================
    #

    print()
    print("=" * 80)
    print("[OuroBuild] RESULTADO")
    print("=" * 80)

    print(
        "[OuroBuild] Arquivos analisados:"
    )

    print(
        f"[OuroBuild] {result.files_analyzed}"
    )

    print(
        "[OuroBuild] Arquivos que seriam removidos:"
    )

    print(
        f"[OuroBuild] {len(result.files_removed)}"
    )

    print(
        "[OuroBuild] Arquivos preservados:"
    )

    print(
        f"[OuroBuild] {len(result.files_preserved)}"
    )

    print(
        "[OuroBuild] Diretórios analisados:"
    )

    print(
        f"[OuroBuild] {result.directories_analyzed}"
    )

    print(
        "[OuroBuild] Diretórios que seriam removidos:"
    )

    print(
        f"[OuroBuild] {len(result.directories_removed)}"
    )

    print(
        "[OuroBuild] Diretórios preservados:"
    )

    print(
        f"[OuroBuild] {len(result.directories_preserved)}"
    )

    print("=" * 80)

    #
    # ========================================================
    # Arquivos que seriam removidos.
    # ========================================================
    #

    print()
    print(
        "[OuroBuild] ARQUIVOS QUE SERIAM REMOVIDOS"
    )

    print("-" * 80)

    for path in result.files_removed:

        print(
            f"[REMOVE] {path}"
        )

    #
    # ========================================================
    # Arquivos preservados.
    # ========================================================
    #

    print()
    print(
        "[OuroBuild] ARQUIVOS PRESERVADOS"
    )

    print("-" * 80)

    for path in result.files_preserved:

        if (
            path.name.lower().endswith(
                ".config"
            )
        ):

            print(
                f"[PRESERVE CONFIG] {path}"
            )

    #
    # ========================================================
    # Diretórios que seriam removidos.
    # ========================================================
    #

    print()
    print(
        "[OuroBuild] DIRETÓRIOS QUE SERIAM REMOVIDOS"
    )

    print("-" * 80)

    for path in result.directories_removed:

        print(
            f"[REMOVE DIRECTORY] {path}"
        )

    #
    # ========================================================
    # Diretórios preservados.
    # ========================================================
    #

    print()
    print(
        "[OuroBuild] DIRETÓRIOS PRESERVADOS"
    )

    print("-" * 80)

    for path in result.directories_preserved:

        if (
            path.name.lower()
            == "xml"
        ):

            print(
                f"[PRESERVE DIRECTORY] {path}"
            )

    #
    # ========================================================
    # Erros.
    # ========================================================
    #

    print()
    print("=" * 80)

    if result.errors:

        print(
            "[OuroBuild] ERROS"
        )

        print("-" * 80)

        for error in result.errors:

            print(
                f"[ERROR] {error}"
            )

    else:

        print(
            "[OuroBuild] Nenhum erro."
        )

    print("=" * 80)

    print()
    print(
        "[OuroBuild] DRY RUN FINALIZADO."
    )

    print(
        "[OuroBuild] Nenhum arquivo ou diretório foi alterado."
    )

    print("=" * 80)


if __name__ == "__main__":
    main()