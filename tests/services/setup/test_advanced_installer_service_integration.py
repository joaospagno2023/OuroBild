"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_build_integration.py
Descrição : Teste de integração do Build do Advanced Installer
            utilizando o AIP real do LinkPagamento.
--------------------------------------------------------------------
"""

import shutil

from pathlib import Path

from app.models.process.command import (
    Command,
)

from app.models.process.command_argument import (
    CommandArgument,
)

from app.models.process.process_status import (
    ProcessStatus,
)

from app.services.process_service import (
    DefaultProcessService,
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


ADVANCED_INSTALLER_PATH = Path(
    r"C:\Program Files (x86)"
    r"\Caphyon"
    r"\Advanced Installer 21.9"
    r"\bin"
    r"\x86"
    r"\AdvancedInstaller.com"
)


TEST_VERSION = "99.99.99.0"


def test_deve_executar_refresh_sync_e_build_no_aip_real(
    tmp_path: Path,
):
    """
    Deve executar RefreshSync e Build utilizando
    o AIP real do LinkPagamento.

    O AIP original nunca deve ser alterado.
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
    # 3. Validar Advanced Installer.
    # ============================================================
    #

    if not ADVANCED_INSTALLER_PATH.exists():

        raise FileNotFoundError(
            "AdvancedInstaller.com não encontrado:\n"
            f"{ADVANCED_INSTALLER_PATH}"
        )

    if not ADVANCED_INSTALLER_PATH.is_file():

        raise ValueError(
            "AdvancedInstaller.com não é um arquivo:\n"
            f"{ADVANCED_INSTALLER_PATH}"
        )

    #
    # ============================================================
    # 4. Criar cópia temporária do AIP.
    # ============================================================
    #

    temporary_aip = (
        tmp_path
        / AIP_PATH.name
    )

    shutil.copy2(
        AIP_PATH,
        temporary_aip,
    )

    #
    # ============================================================
    # 5. Tornar a cópia gravável.
    #
    # Arquivos provenientes do TFS/TFVC podem estar
    # somente leitura.
    # ============================================================
    #

    temporary_aip.chmod(
        temporary_aip.stat().st_mode
        | 0o200
    )

    #
    # ============================================================
    # 6. Preparar o AIP.
    #
    # Utilizamos o modificador já validado.
    # ============================================================
    #

    from app.services.setup.advanced_installer_aip_modifier import (
        AdvancedInstallerAipModifier,
    )

    modifier = (
        AdvancedInstallerAipModifier()
    )

    modifier.apply(
        aip_path=temporary_aip,
        version=TEST_VERSION,
        publish_path=PUBLISH_PATH,
    )

    #
    # ============================================================
    # 7. Validar alteração da versão.
    # ============================================================
    #

    prepared_content = (
        temporary_aip.read_text(
            encoding="utf-8",
        )
    )

    assert (
        f'Value="{TEST_VERSION}"'
        in prepared_content
    )

    #
    # ============================================================
    # 8. Criar ProcessService real.
    # ============================================================
    #

    process_service = (
        DefaultProcessService()
    )

    #
    # ============================================================
    # 9. Executar RefreshSync.
    # ============================================================
    #

    refresh_sync_command = Command(
        executable=(
            ADVANCED_INSTALLER_PATH
        ),
        working_directory=(
            temporary_aip.parent
        ),
        arguments=[
            CommandArgument(
                value="/edit",
            ),
            CommandArgument(
                value=str(
                    temporary_aip
                ),
            ),
            CommandArgument(
                value="/RefreshSync",
            ),
        ],
    )

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] ADVANCED INSTALLER - REFRESH SYNC"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] Executável:"
    )

    print(
        f"[OuroBuild] {ADVANCED_INSTALLER_PATH}"
    )

    print(
        "[OuroBuild] AIP:"
    )

    print(
        f"[OuroBuild] {temporary_aip}"
    )

    print(
        "[OuroBuild] Origem:"
    )

    print(
        f"[OuroBuild] {PUBLISH_PATH}"
    )

    print(
        "[OuroBuild] Versão:"
    )

    print(
        f"[OuroBuild] {TEST_VERSION}"
    )

    print(
        "=" * 80
    )

    refresh_sync_result = (
        process_service.execute(
            refresh_sync_command,
        )
    )

    print()
    print(
        "[OuroBuild] RefreshSync ExitCode:"
    )

    print(
        f"[OuroBuild] "
        f"{refresh_sync_result.exit_code}"
    )

    print()
    print(
        "[OuroBuild] RefreshSync STDOUT:"
    )

    print(
        refresh_sync_result.stdout
    )

    print()
    print(
        "[OuroBuild] RefreshSync STDERR:"
    )

    print(
        refresh_sync_result.stderr
    )

    assert (
        refresh_sync_result.status
        == ProcessStatus.SUCCESS
    ), (
        "O Advanced Installer retornou erro "
        "durante o RefreshSync.\n\n"
        f"ExitCode: "
        f"{refresh_sync_result.exit_code}\n\n"
        f"STDOUT:\n"
        f"{refresh_sync_result.stdout}\n\n"
        f"STDERR:\n"
        f"{refresh_sync_result.stderr}"
    )

    #
    # ============================================================
    # 10. Executar Build.
    # ============================================================
    #

    build_command = Command(
        executable=(
            ADVANCED_INSTALLER_PATH
        ),
        working_directory=(
            temporary_aip.parent
        ),
        arguments=[
            CommandArgument(
                value="/build",
            ),
            CommandArgument(
                value=str(
                    temporary_aip
                ),
            ),
        ],
    )

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] ADVANCED INSTALLER - BUILD"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] Executável:"
    )

    print(
        f"[OuroBuild] {ADVANCED_INSTALLER_PATH}"
    )

    print(
        "[OuroBuild] AIP:"
    )

    print(
        f"[OuroBuild] {temporary_aip}"
    )

    print(
        "[OuroBuild] Comando:"
    )

    print(
        "[OuroBuild] "
        f'"{ADVANCED_INSTALLER_PATH}" '
        f'/build '
        f'"{temporary_aip}"'
    )

    print(
        "=" * 80
    )

    build_result = (
        process_service.execute(
            build_command,
        )
    )

    print()
    print(
        "[OuroBuild] Build ExitCode:"
    )

    print(
        f"[OuroBuild] "
        f"{build_result.exit_code}"
    )

    print()
    print(
        "[OuroBuild] Build STDOUT:"
    )

    print(
        build_result.stdout
    )

    print()
    print(
        "[OuroBuild] Build STDERR:"
    )

    print(
        build_result.stderr
    )

    #
    # ============================================================
    # 11. Validar Build.
    # ============================================================
    #

    assert (
        build_result.status
        == ProcessStatus.SUCCESS
    ), (
        "O Advanced Installer retornou erro "
        "durante o Build.\n\n"
        f"ExitCode: "
        f"{build_result.exit_code}\n\n"
        f"STDOUT:\n"
        f"{build_result.stdout}\n\n"
        f"STDERR:\n"
        f"{build_result.stderr}"
    )

    #
    # ============================================================
    # 12. Resolver MSI.
    #
    # O AIP define o nome do produto como:
    #
    # OuroNetWinServiceLinkPagamento
    #
    # e o BuildName utiliza:
    #
    # [ProductName].Setup
    #
    # O PATHFOLDER é relativo ao AIP.
    #
    # Portanto, procuramos o MSI gerado a partir
    # do diretório temporário.
    # ============================================================
    #

    expected_file_name = (
        "OuroNetWinServiceLinkPagamento.Setup.msi"
    )

    possible_msi_paths = [
        temporary_aip.parent
        / expected_file_name,

        temporary_aip.parent
        / "Setups"
        / expected_file_name,

        temporary_aip.parent.parent
        / "Setups"
        / expected_file_name,
    ]

    output_msi = None

    for candidate in possible_msi_paths:

        if candidate.exists():

            output_msi = candidate

            break

    #
    # ============================================================
    # 13. Caso não seja encontrado no caminho esperado,
    # procurar dentro do diretório temporário.
    # ============================================================
    #

    if output_msi is None:

        generated_files = list(
            tmp_path.rglob(
                "*.msi"
            )
        )

        if generated_files:

            output_msi = (
                generated_files[0]
            )

    #
    # ============================================================
    # 14. Validar MSI.
    # ============================================================
    #

    assert output_msi is not None, (
        "O Build terminou com sucesso, "
        "porém nenhum arquivo MSI foi encontrado.\n\n"
        f"Temporary AIP: "
        f"{temporary_aip}\n\n"
        f"STDOUT:\n"
        f"{build_result.stdout}\n\n"
        f"STDERR:\n"
        f"{build_result.stderr}"
    )

    assert output_msi.exists()

    assert output_msi.is_file()

    assert (
        output_msi.stat().st_size > 0
    )

    #
    # ============================================================
    # 15. O AIP temporário deve continuar existindo.
    # ============================================================
    #

    assert (
        temporary_aip.exists()
    )

    #
    # ============================================================
    # 16. O AIP original deve continuar intacto.
    # ============================================================
    #

    original_content = (
        AIP_PATH.read_text(
            encoding="utf-8",
        )
    )

    assert (
        f'Value="{TEST_VERSION}"'
        not in original_content
    )

    #
    # ============================================================
    # 17. Diagnóstico final.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] BUILD CONCLUÍDO"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] RefreshSync: OK"
    )

    print(
        "[OuroBuild] Build: OK"
    )

    print(
        "[OuroBuild] MSI:"
    )

    print(
        f"[OuroBuild] {output_msi}"
    )

    print(
        "[OuroBuild] "
        "O AIP original permaneceu intacto."
    )

    print(
        "=" * 80
    )