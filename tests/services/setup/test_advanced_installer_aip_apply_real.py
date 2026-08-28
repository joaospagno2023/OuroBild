"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_aip_apply_real.py
Descrição : Teste de integração do Parser, Comparator e Modifier
            utilizando o AIP real do LinkPagamento.
--------------------------------------------------------------------
"""

import shutil

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


TEST_VERSION = "99.99.99.0"


def test_deve_aplicar_adds_reais_no_aip_temporario(
    tmp_path: Path,
):
    """
    Deve:

        1. copiar o AIP real;
        2. executar o Parser;
        3. executar o Comparator;
        4. obter os ADDs reais;
        5. aplicar os ADDs no AIP temporário;
        6. preservar o AIP original.

    O Advanced Installer não é executado neste teste.
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
    # 3. Guardar conteúdo original.
    # ============================================================
    #

    original_content = (
        AIP_PATH.read_text(
            encoding="utf-8",
        )
    )

    #
    # ============================================================
    # 4. Criar cópia temporária.
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

    temporary_aip.chmod(
        temporary_aip.stat().st_mode
        | 0o200
    )

    #
    # ============================================================
    # 5. Ler AIP temporário.
    # ============================================================
    #

    content = (
        temporary_aip.read_text(
            encoding="utf-8",
        )
    )

    #
    # ============================================================
    # 6. Executar Parser.
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
    # 7. Executar Comparator.
    # ============================================================
    #

    comparator = (
        AdvancedInstallerAipFileComparator()
    )

    changes = (
        comparator.compare(
            aip_files=aip_files,
            publish_path=PUBLISH_PATH,
        )
    )

    #
    # ============================================================
    # 8. Separar alterações.
    # ============================================================
    #

    add_changes = [
        change
        for change in changes
        if change.action
        == SetupFileAction.ADD
    ]

    remove_changes = [
        change
        for change in changes
        if change.action
        == SetupFileAction.REMOVE
    ]

    keep_changes = [
        change
        for change in changes
        if change.action
        == SetupFileAction.KEEP
    ]

    #
    # ============================================================
    # 9. Diagnóstico do Comparator.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] ALTERAÇÕES REAIS"
    )

    print(
        "=" * 80
    )

    print(
        f"[OuroBuild] AIP: {len(aip_files)}"
    )

    print(
        f"[OuroBuild] KEEP: {len(keep_changes)}"
    )

    print(
        f"[OuroBuild] ADD: {len(add_changes)}"
    )

    print(
        f"[OuroBuild] REMOVE: {len(remove_changes)}"
    )

    #
    # ============================================================
    # 10. Validar cenário conhecido.
    #
    # Na análise anterior tivemos:
    #
    #     AIP    = 591
    #     KEEP   = 591
    #     ADD    = 66
    #     REMOVE = 0
    #
    # Não vamos exigir quantidade fixa de KEEP/ADD caso o Release
    # seja alterado posteriormente.
    #
    # Porém, neste momento esperamos os 66 ADD identificados
    # anteriormente.
    # ============================================================
    #

    assert len(
        aip_files
    ) == 591

    assert len(
        keep_changes
    ) == 591

    assert len(
        add_changes
    ) == 66

    assert len(
        remove_changes
    ) == 0

    #
    # ============================================================
    # 11. Aplicar alterações no AIP temporário.
    # ============================================================
    #

    modifier = (
        AdvancedInstallerAipModifier()
    )

    modifier.apply(
        aip_path=temporary_aip,
        version=TEST_VERSION,
        publish_path=PUBLISH_PATH,
        changes=changes,
    )

    #
    # ============================================================
    # 12. Ler AIP modificado.
    # ============================================================
    #

    modified_content = (
        temporary_aip.read_text(
            encoding="utf-8",
        )
    )

    #
    # ============================================================
    # 13. Validar versão.
    # ============================================================
    #

    assert (
        f'Value="{TEST_VERSION}"'
        in modified_content
    )

    #
    # ============================================================
    # 14. Validar todos os ADDs.
    # ============================================================
    #

    for change in add_changes:

        assert (
            f'File="{change.name}"'
            in modified_content
        )

        assert (
            f'SourcePath="{change.source_path}"'
            in modified_content
        )

    #
    # ============================================================
    # 15. Contar os arquivos adicionados.
    #
    # Cada ADD deve produzir exatamente um ROW.
    # ============================================================
    #

    for change in add_changes:

        occurrences = (
            modified_content.count(
                f'File="{change.name}"'
            )
        )

        assert (
            occurrences == 1
        ), (
            "O arquivo ADD não foi inserido "
            "exatamente uma vez:\n"
            f"{change.name}\n"
            f"Ocorrências: {occurrences}"
        )

    #
    # ============================================================
    # 16. Confirmar que os arquivos existentes continuam.
    # ============================================================
    #

    for setup_file in aip_files:

        assert (
            setup_file.name
            in modified_content
        )

    #
    # ============================================================
    # 17. O AIP temporário deve existir.
    # ============================================================
    #

    assert (
        temporary_aip.exists()
    )

    #
    # ============================================================
    # 18. O AIP original deve permanecer intacto.
    # ============================================================
    #

    current_original_content = (
        AIP_PATH.read_text(
            encoding="utf-8",
        )
    )

    assert (
        current_original_content
        == original_content
    )

    assert (
        f'Value="{TEST_VERSION}"'
        not in current_original_content
    )

    #
    # ============================================================
    # 19. Diagnóstico final.
    # ============================================================
    #

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] APLICAÇÃO CONCLUÍDA"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] Parser: OK"
    )

    print(
        "[OuroBuild] Comparator: OK"
    )

    print(
        "[OuroBuild] Modifier: OK"
    )

    print(
        f"[OuroBuild] ADD aplicados: "
        f"{len(add_changes)}"
    )

    print(
        "[OuroBuild] AIP original: intacto"
    )

    print(
        f"[OuroBuild] AIP temporário: "
        f"{temporary_aip}"
    )

    print(
        "=" * 80
    )