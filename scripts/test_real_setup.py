"""
--------------------------------------------------------------------
Projeto : OuroBuild

Arquivo : test_real_setup.py

Descrição : Executa a geração real de um Setup através do fluxo
            completo do OuroBuild.

            Este script utiliza a mesma composição da aplicação:

                Bootstrap
                    ↓
                ExecuteSetupUseCase
                    ↓
                SetupOrchestrator
                    ↓
                SetupFactory
                    ↓
                AdvancedInstallerService
                    ↓
                AIP Synchronizer
                    ↓
                RefreshSync
                    ↓
                Build
                    ↓
                MSI

Projeto utilizado neste teste:

    linkpagamento

Ambiente:

    production

A versão é informada pela linha de comando para evitar que o script
invente ou sobrescreva a versão desejada pelo usuário.

Exemplo:

    python .\\scripts\\test_real_setup.py 10.4.0

Com revision:

    python .\\scripts\\test_real_setup.py 10.4.0 1
--------------------------------------------------------------------
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.bootstrap import Bootstrap
from app.models.setup.setup_request import SetupRequest


PROJECT_ID = "wcfmovimento"
ENVIRONMENT_ID = "production"


def parse_arguments() -> argparse.Namespace:
    """Lê os argumentos da execução real do Setup."""

    parser = argparse.ArgumentParser(
        description=(
            "Executa a geração real do Setup do "
            "WinService LinkPagamento."
        ),
    )

    parser.add_argument(
        "version",
        help="Versão que será aplicada ao Setup. Exemplo: 10.4.0",
    )

    parser.add_argument(
        "revision",
        nargs="?",
        type=int,
        default=None,
        help="Revision opcional da geração do Setup.",
    )

    return parser.parse_args()


def main() -> int:
    """Executa a geração real do Setup."""

    arguments = parse_arguments()

    request = SetupRequest(
        project_id=PROJECT_ID,
        environment_id=ENVIRONMENT_ID,
        version=arguments.version,
        revision=arguments.revision,
    )

    print()
    print("=" * 80)
    print("[OuroBuild] GERAÇÃO REAL DE SETUP")
    print("=" * 80)
    print(f"[OuroBuild] Projeto     : {request.project_id}")
    print(f"[OuroBuild] Ambiente    : {request.environment_id}")
    print(f"[OuroBuild] Versão      : {request.version}")
    print(f"[OuroBuild] Revision    : {request.revision}")
    print("[OuroBuild] Engine      : Advanced Installer")
    print("=" * 80)
    print()

    bootstrap = Bootstrap()
    use_case = bootstrap.execute_setup_use_case

    result = use_case.execute(request)

    print()
    print("=" * 80)
    print("[OuroBuild] RESULTADO DA GERAÇÃO")
    print("=" * 80)
    print(f"[OuroBuild] Sucesso     : {result.success}")
    print(f"[OuroBuild] Projeto     : {result.project_id}")
    print(f"[OuroBuild] Mensagem    : {result.message}")
    print(f"[OuroBuild] MSI         : {result.output_msi}")
    print(f"[OuroBuild] Duração     : {result.duration_seconds:.2f}s")

    if result.steps:
        print()
        print("[OuroBuild] ETAPAS")

        for step in result.steps:
            print(
                f"[OuroBuild] {step.name:<12} : {step.status.value}"
            )

            if step.message:
                print(
                    f"[OuroBuild]   Mensagem: {step.message}"
                )

            if step.errors:
                print("[OuroBuild]   Erros:")

                for error in step.errors:
                    print(
                        f"[OuroBuild]     - {error}"
                    )

    print("=" * 80)
    print()

    if not result.success:
        return 1

    if result.output_msi is None:
        print(
            "[OuroBuild] ERRO: a geração foi marcada como sucesso, "
            "mas nenhum MSI foi informado."
        )
        return 1

    output_msi = Path(result.output_msi)

    if not output_msi.exists():
        print(
            "[OuroBuild] ERRO: o MSI informado pelo resultado "
            "não existe no disco:"
        )
        print(f"[OuroBuild] {output_msi}")
        return 1

    if not output_msi.is_file():
        print(
            "[OuroBuild] ERRO: o caminho do MSI não é um arquivo:"
        )
        print(f"[OuroBuild] {output_msi}")
        return 1

    print("[OuroBuild] MSI gerado e localizado com sucesso:")
    print(f"[OuroBuild] {output_msi.resolve()}")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
