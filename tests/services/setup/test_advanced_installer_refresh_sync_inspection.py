"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_refresh_sync_inspection.py
Descrição : Inspeção do AIP real após o RefreshSync.
--------------------------------------------------------------------
"""

import shutil
import subprocess

from pathlib import Path

from app.services.setup.advanced_installer_aip_modifier import (
    AdvancedInstallerAipModifier,
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


def test_deve_inspecionar_aip_apos_refresh_sync(
    tmp_path: Path,
):
    """
    Executa o RefreshSync e preserva uma cópia do AIP
    temporário para inspeção.

    O AIP original nunca é alterado.
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
        "Pasta Release não encontrada:\n"
        f"{PUBLISH_PATH}"
    )

    assert ADVANCED_INSTALLER_PATH.exists(), (
        "AdvancedInstaller.com não encontrado:\n"
        f"{ADVANCED_INSTALLER_PATH}"
    )

    #
    # ============================================================
    # 2. Criar AIP temporário.
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
    # Arquivos do TFS/TFVC podem ser somente leitura.
    #

    temporary_aip.chmod(
        temporary_aip.stat().st_mode
        | 0o200
    )

    #
    # ============================================================
    # 3. Preparar AIP.
    # ============================================================
    #

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
    # 4. Validar preparação antes do Advanced Installer.
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
    # O AIP preparado deve conter a definição de
    # pasta sincronizada.
    #

    assert (
        "SynchronizedFolderComponent"
        in prepared_content
    )

    #
    # ============================================================
    # 5. Executar RefreshSync.
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
        "[OuroBuild] REFRESH SYNC - INSPEÇÃO"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] AIP temporário:"
    )

    print(
        temporary_aip
    )

    print(
        "[OuroBuild] Origem:"
    )

    print(
        PUBLISH_PATH
    )

    print(
        "[OuroBuild] Versão:"
    )

    print(
        TEST_VERSION
    )

    print(
        "[OuroBuild] Comando:"
    )

    print(
        " ".join(
            (
                f'"{value}"'
                if " " in value
                else value
            )
            for value in command
        )
    )

    print(
        "=" * 80
    )

    result = subprocess.run(
        command,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    #
    # ============================================================
    # 6. Diagnóstico do processo.
    # ============================================================
    #

    print()
    print(
        "[OuroBuild] EXIT CODE:"
    )

    print(
        result.returncode
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
    # 7. Validar sucesso do RefreshSync.
    # ============================================================
    #

    assert (
        result.returncode == 0
    ), (
        "RefreshSync falhou.\n\n"
        f"ExitCode: {result.returncode}\n\n"
        f"STDOUT:\n{result.stdout}\n\n"
        f"STDERR:\n{result.stderr}"
    )

    #
    # ============================================================
    # 8. Ler AIP após o RefreshSync.
    # ============================================================
    #

    assert (
        temporary_aip.exists()
    )

    content = (
        temporary_aip.read_text(
            encoding="utf-8",
        )
    )

    #
    # ============================================================
    # 9. Validar versão.
    # ============================================================
    #

    assert (
        f'Value="{TEST_VERSION}"'
        in content
    )

    #
    # ============================================================
    # 10. O AIP deve continuar contendo a estrutura
    # de pasta sincronizada.
    # ============================================================
    #

    assert (
        "SynchronizedFolderComponent"
        in content
    )

    #
    # ============================================================
    # 11. Validar a execução pela saída do Advanced Installer.
    #
    # Não verificamos o SourcePath diretamente no XML/AIP,
    # pois o Advanced Installer pode reescrever a representação
    # interna depois do RefreshSync.
    #
    # A saída oficial do comando é a fonte correta para saber
    # qual pasta foi sincronizada.
    # ============================================================
    #

    normalized_stdout = (
        result.stdout
        .replace(
            "/",
            "\\",
        )
    )

    normalized_publish_path = (
        str(
            PUBLISH_PATH.resolve()
        )
        .replace(
            "/",
            "\\",
        )
    )

    assert (
        normalized_publish_path.lower()
        in normalized_stdout.lower()
    ), (
        "O Advanced Installer não informou a "
        "sincronização da pasta esperada.\n\n"
        f"Pasta esperada:\n"
        f"{normalized_publish_path}\n\n"
        f"STDOUT:\n"
        f"{result.stdout}"
    )

    #
    # ============================================================
    # 12. Validar arquivos conhecidos adicionados.
    # ============================================================
    #

    expected_files = [
        "OuroNetWinServiceLinkPagamento.pdb",
        "OuroNet.Client.WinService.Business.pdb",
        "OuroNet.Server.Common.pdb",
        "OuroNet.Server.Entities.pdb",
        "OuroNet.Server.ServiceInterfaces.pdb",
    ]

    for file_name in expected_files:

        assert (
            f'APPDIR\\{file_name}'
            in result.stdout
        ), (
            "O arquivo esperado não apareceu "
            "na sincronização do Advanced Installer:\n"
            f"{file_name}"
        )

    #
    # ============================================================
    # 13. Localizar SourcePath no AIP.
    #
    # Aqui apenas exibimos.
    #
    # NÃO fazemos assert porque queremos descobrir
    # exatamente como o Advanced Installer serializa
    # essa informação depois do RefreshSync.
    # ============================================================
    #

    source_path_lines = [
        line
        for line in content.splitlines()
        if "SourcePath" in line
    ]

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] SOURCEPATH ENCONTRADOS NO AIP"
    )

    print(
        "=" * 80
    )

    if source_path_lines:

        for line in source_path_lines:

            print(
                line
            )

    else:

        print(
            "[OuroBuild] Nenhum SourcePath encontrado."
        )

    print(
        "=" * 80
    )

    #
    # ============================================================
    # 14. Localizar estruturas relacionadas à sincronização.
    # ============================================================
    #

    synchronized_lines = [
        line
        for line in content.splitlines()
        if (
            "SynchronizedFolder"
            in line
            or "Synchroniz"
            in line
            or "APPDIR"
            in line
        )
    ]

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] ESTRUTURAS DE SINCRONIZAÇÃO"
    )

    print(
        "=" * 80
    )

    for line in synchronized_lines:

        print(
            line
        )

    print(
        "=" * 80
    )

    #
    # ============================================================
    # 15. Gerar arquivo completo para inspeção.
    # ============================================================
    #

    inspection_path = (
        tmp_path
        / "AIP_AFTER_REFRESH_SYNC.txt"
    )

    inspection_path.write_text(
        content,
        encoding="utf-8",
    )

    #
    # ============================================================
    # 16. Estatísticas.
    # ============================================================
    #

    lines = content.splitlines()

    component_count = sum(
        1
        for line in lines
        if "<COMPONENT" in line
    )

    appdir_reference_count = sum(
        1
        for line in lines
        if "APPDIR\\" in line
    )

    synchronized_count = sum(
        1
        for line in lines
        if "SynchronizedFolder" in line
    )

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] ESTATÍSTICAS DO AIP"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] Componentes:"
    )

    print(
        component_count
    )

    print(
        "[OuroBuild] Referências APPDIR:"
    )

    print(
        appdir_reference_count
    )

    print(
        "[OuroBuild] Estruturas SynchronizedFolder:"
    )

    print(
        synchronized_count
    )

    print(
        "[OuroBuild] Arquivo de inspeção:"
    )

    print(
        inspection_path
    )

    print(
        "=" * 80
    )

    #
    # ============================================================
    # 17. Validar que o AIP original não foi alterado.
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
    # 18. Resultado final.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] REFRESH SYNC VALIDADO"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] AIP original permaneceu intacto."
    )

    print(
        "[OuroBuild] RefreshSync retornou código 0."
    )

    print(
        "[OuroBuild] Arquivos esperados foram sincronizados."
    )

    print(
        "=" * 80
    )
