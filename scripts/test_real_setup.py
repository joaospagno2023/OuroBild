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

O projeto e o ambiente são informados pela linha de comando,
permitindo executar o fluxo real para qualquer projeto
cadastrado em projects.json.

A versão é informada pela linha de comando para evitar que o
script invente ou sobrescreva a versão desejada pelo usuário.

Exemplo:

    python .\\scripts\\test_real_setup.py linkpagamento 10.4.0

Com revision:

    python .\\scripts\\test_real_setup.py linkpagamento 10.4.0 1

Com ambiente explícito:

    python .\\scripts\\test_real_setup.py linkpagamento 10.4.7 2 --environment versioned

Compatibilidade:

    Quando o primeiro argumento não corresponder a um
    project_id conhecido (ex.: já for a versão, no formato
    antigo do script), o projeto padrão "linkpagamento"
    é utilizado automaticamente.

Regra do ambiente versionado:

    Versão do Setup:
        10.4.7

    Workspace físico:
        10.4\\7

    Revision da execução:
        2
--------------------------------------------------------------------
"""

from __future__ import annotations

import argparse
import re
import sys

from pathlib import Path


PROJECT_ROOT = Path(
    __file__,
).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.bootstrap import Bootstrap
from app.models.setup.setup_request import SetupRequest


DEFAULT_PROJECT_ID = "linkpagamento"
DEFAULT_ENVIRONMENT_ID = "production"


#
# Um identificador de versão sempre contém ao menos
# dois pontos ou um ponto, por exemplo:
#
#   10.4.7
#   10.7.2
#
# Isso é usado apenas para manter compatibilidade
# com o formato antigo do script.
#

_VERSION_PATTERN = re.compile(
    r"^\d+(\.\d+)+$",
)


def parse_arguments() -> argparse.Namespace:
    """Lê os argumentos da execução real do Setup."""

    parser = argparse.ArgumentParser(
        description=(
            "Executa a geração real do Setup de um "
            "projeto configurado no OuroBuild."
        ),
    )

    parser.add_argument(
        "project_or_version",
        help=(
            "Identificador do projeto (project_id do "
            "projects.json). Por compatibilidade, se este "
            "argumento já for uma versão (ex.: 10.4.0), o "
            f"projeto padrão '{DEFAULT_PROJECT_ID}' é "
            "utilizado."
        ),
    )

    parser.add_argument(
        "version_or_revision",
        nargs="?",
        default=None,
        help=(
            "Versão que será aplicada ao Setup. Exemplo: "
            "10.4.0. Quando o primeiro argumento já for a "
            "versão (modo de compatibilidade), este "
            "argumento é tratado como a revision."
        ),
    )

    parser.add_argument(
        "revision",
        nargs="?",
        type=int,
        default=None,
        help="Revision opcional da geração do Setup.",
    )

    parser.add_argument(
        "--environment",
        dest="environment_id",
        default=DEFAULT_ENVIRONMENT_ID,
        help=(
            "Identificador do ambiente (environment_id do "
            f"environments.json). Padrão: "
            f"'{DEFAULT_ENVIRONMENT_ID}'."
        ),
    )

    return parser.parse_args()


def resolve_request_arguments(
    arguments: argparse.Namespace,
) -> tuple[str, str, int | None]:
    """
    Resolve project_id, version e revision a partir dos
    argumentos recebidos, preservando compatibilidade com
    o formato antigo do script (onde o primeiro argumento
    já era a versão).
    """

    #
    # Modo de compatibilidade:
    #
    #     test_real_setup.py 10.4.0
    #     test_real_setup.py 10.4.0 1
    #
    # O primeiro argumento já é a versão.
    #

    if _VERSION_PATTERN.match(
        arguments.project_or_version,
    ):
        project_id = DEFAULT_PROJECT_ID

        version = (
            arguments.project_or_version
        )

        revision = (
            int(arguments.version_or_revision)
            if arguments.version_or_revision is not None
            else None
        )

        return (
            project_id,
            version,
            revision,
        )

    #
    # Modo atual:
    #
    #     test_real_setup.py <project_id> <version>
    #     test_real_setup.py <project_id> <version> <revision>
    #

    project_id = (
        arguments.project_or_version
    )

    if arguments.version_or_revision is None:
        raise SystemExit(
            "[OuroBuild] ERRO: a versão do Setup não foi "
            "informada.\n"
            "Uso: python .\\scripts\\test_real_setup.py "
            "<project_id> <version> [revision]"
        )

    version = (
        arguments.version_or_revision
    )

    revision = arguments.revision

    return (
        project_id,
        version,
        revision,
    )


def build_workspace_version(
    version: str,
) -> str:
    """
    Converte a versão lógica do Setup para o formato
    físico utilizado pelo workspace versionado.

    Exemplo:

        10.4.7
        ↓
        10.4\\7

    Importante:

        Esta função NÃO altera a versão do Setup.

        A versão continua sendo:

            10.4.7

        Apenas a representação do diretório físico
        é transformada para:

            10.4\\7
    """

    normalized_version = (
        version.strip()
    )

    parts = (
        normalized_version.split(".")
    )

    if len(parts) < 3:
        return normalized_version

    version_root = ".".join(
        parts[:-1],
    )

    version_build = parts[-1]

    return (
        f"{version_root}\\{version_build}"
    )


def main() -> int:
    """Executa a geração real do Setup."""

    arguments = parse_arguments()

    project_id, version, revision = (
        resolve_request_arguments(
            arguments,
        )
    )

    environment_id = (
        arguments.environment_id
    )

    request = SetupRequest(
        project_id=project_id,
        environment_id=environment_id,
        version=version,
        revision=revision,
    )

    workspace_version = (
        build_workspace_version(
            request.version or "",
        )
    )

    print()

    print("=" * 80)
    print("[OuroBuild] GERAÇÃO REAL DE SETUP")
    print("=" * 80)

    print(
        f"[OuroBuild] Projeto                 : "
        f"{request.project_id}"
    )

    print(
        f"[OuroBuild] Ambiente                : "
        f"{request.environment_id}"
    )

    print(
        f"[OuroBuild] VERSÃO DO SETUP         : "
        f"{request.version}"
    )

    print(
        f"[OuroBuild] REVISION DA EXECUÇÃO    : "
        f"{request.revision}"
    )

    print(
        f"[OuroBuild] WORKSPACE VERSIONADO    : "
        f"{workspace_version}"
    )

    print(
        f"[OuroBuild] VERSÃO LEVADA AO FLUXO : "
        f"{request.version}"
    )

    print(
        "[OuroBuild] Engine                  : "
        "Advanced Installer"
    )

    print("=" * 80)
    print()

    bootstrap = Bootstrap()

    use_case = (
        bootstrap.execute_setup_use_case
    )

    result = use_case.execute(
        request,
    )

    print()

    print("=" * 80)
    print("[OuroBuild] RESULTADO DA GERAÇÃO")
    print("=" * 80)

    print(
        f"[OuroBuild] Sucesso     : "
        f"{result.success}"
    )

    print(
        f"[OuroBuild] Projeto     : "
        f"{result.project_id}"
    )

    print(
        f"[OuroBuild] Mensagem    : "
        f"{result.message}"
    )

    print(
        f"[OuroBuild] MSI         : "
        f"{result.output_msi}"
    )

    print(
        f"[OuroBuild] Duração     : "
        f"{result.duration_seconds:.2f}s"
    )

    print("=" * 80)
    print()

    if not result.success:
        return 1

    if result.output_msi is None:
        print(
            "[OuroBuild] ERRO: a geração foi marcada como "
            "sucesso, mas nenhum MSI foi informado."
        )

        return 1

    output_msi = Path(
        result.output_msi,
    )

    if not output_msi.exists():
        print(
            "[OuroBuild] ERRO: o MSI informado pelo "
            "resultado não existe no disco:"
        )

        print(
            f"[OuroBuild] {output_msi}"
        )

        return 1

    if not output_msi.is_file():
        print(
            "[OuroBuild] ERRO: o caminho do MSI "
            "não é um arquivo:"
        )

        print(
            f"[OuroBuild] {output_msi}"
        )

        return 1

    print(
        "[OuroBuild] MSI gerado e localizado "
        "com sucesso:"
    )

    print(
        f"[OuroBuild] "
        f"{output_msi.resolve()}"
    )

    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(),
    )