"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_refresh_sync.py
Descrição : Teste de integração do RefreshSync do Advanced Installer
            utilizando o AIP real do LinkPagamento.
--------------------------------------------------------------------
"""

import shutil
import subprocess

from pathlib import Path


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
    r"\Advanced Installer 23.7"
    r"\bin"
    r"\x86"
    r"\AdvancedInstaller.com"
)


TEST_VERSION = "99.99.99.0"


def test_deve_executar_refresh_sync_no_aip_real(
    tmp_path: Path,
):
    """
    Deve executar o RefreshSync no AIP real do LinkPagamento.

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
    # Utilizamos o modificador já testado.
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
    # 7. Guardar o conteúdo preparado.
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
    # 8. Executar RefreshSync.
    #
    # O comando é executado diretamente neste teste.
    #
    # Ainda não usamos /rebuild.
    # ============================================================
    #

    command = [
        str(
            ADVANCED_INSTALLER_PATH
        ),
        "/edit",
        str(
            temporary_aip
        ),
        "/RefreshSync",
    ]

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
        "[OuroBuild] Comando:"
    )

    print(
        "[OuroBuild] "
        + " ".join(
            f'"{item}"'
            if " " in item
            else item
            for item in command
        )
    )

    print(
        "=" * 80
    )

    result = subprocess.run(
        command,
        cwd=temporary_aip.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    #
    # ============================================================
    # 9. Exibir diagnóstico.
    # ============================================================
    #

    print()
    print(
        "[OuroBuild] EXIT CODE:"
    )

    print(
        f"[OuroBuild] {result.returncode}"
    )

    print()
    print(
        "[OuroBuild] STDOUT:"
    )

    print(
        result.stdout
    )

    print()
    print(
        "[OuroBuild] STDERR:"
    )

    print(
        result.stderr
    )

    #
    # ============================================================
    # 10. Validar execução.
    # ============================================================
    #

    assert (
        result.returncode == 0
    ), (
        "O Advanced Installer retornou erro "
        "durante o RefreshSync.\n\n"
        f"ExitCode: {result.returncode}\n\n"
        f"STDOUT:\n{result.stdout}\n\n"
        f"STDERR:\n{result.stderr}"
    )

    #
    # ============================================================
    # 11. O AIP temporário deve continuar existindo.
    # ============================================================
    #

    assert (
        temporary_aip.exists()
    )

    #
    # ============================================================
    # 12. O AIP original deve continuar intacto.
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
    # 13. Diagnóstico final.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] REFRESH SYNC CONCLUÍDO"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] O AIP original permaneceu intacto."
    )

    print(
        "[OuroBuild] O RefreshSync retornou sucesso."
    )

    print(
        f"[OuroBuild] AIP temporário: {temporary_aip}"
    )

    print(
        "=" * 80
    )