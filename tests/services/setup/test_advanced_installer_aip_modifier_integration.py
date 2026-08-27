"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_aip_modifier_integration.py
Descrição : Teste de integração do modificador de AIP utilizando
            o projeto real do LinkPagamento.
--------------------------------------------------------------------
"""

import shutil

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


TEST_VERSION = (
    "99.99.99.0"
)


def test_deve_preparar_aip_real_do_linkpagamento(
    tmp_path: Path,
):
    """
    Deve preparar uma cópia do AIP real do LinkPagamento.

    O AIP original nunca deve ser alterado.
    """

    #
    # ============================================================
    # Validação do ambiente.
    # ============================================================
    #

    if not AIP_PATH.exists():

        raise FileNotFoundError(
            "AIP real do LinkPagamento não encontrado:\n"
            f"{AIP_PATH}"
        )

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
    # Copiar AIP real para área temporária.
    # ============================================================
    #

    temporary_aip = (
        tmp_path
        / AIP_PATH.name
    )

    shutil.copyfile(
        AIP_PATH,
        temporary_aip,
    )

    #
    # ============================================================
    # Garantir que a cópia temporária seja gravável.
    #
    # Não devemos alterar os atributos do AIP original.
    # ============================================================
    #

    temporary_aip.chmod(
        0o666,
    )

    #
    # ============================================================
    # Guardar conteúdo original da cópia.
    # ============================================================
    #

    original_content = (
        temporary_aip.read_text(
            encoding="utf-8",
        )
    )

    #
    # ============================================================
    # Executar modificador.
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
    # Ler resultado.
    # ============================================================
    #

    modified_content = (
        temporary_aip.read_text(
            encoding="utf-8",
        )
    )

    #
    # ============================================================
    # Garantir que houve alteração.
    # ============================================================
    #

    assert (
        modified_content
        != original_content
    )

    #
    # ============================================================
    # Validar versão.
    # ============================================================
    #

    assert (
        'Property="ProductVersion"'
        in modified_content
    )

    assert (
        f'Value="{TEST_VERSION}"'
        in modified_content
    )

    #
    # ============================================================
    # Validar pasta de publicação.
    #
    # O AIP utiliza barras invertidas escapadas.
    # ============================================================
    #

    expected_path = (
        str(
            PUBLISH_PATH.resolve(),
        )
        .replace(
            "\\",
            "\\\\",
        )
    )

    assert (
        f'SourcePath="{expected_path}"'
        in modified_content
    )

    #
    # ============================================================
    # Garantir que o AIP original permaneceu intacto.
    # ============================================================
    #

    original_aip_content = (
        AIP_PATH.read_text(
            encoding="utf-8",
        )
    )

    assert (
        original_aip_content
        != modified_content
        or original_aip_content
        == original_content
    )

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] TESTE AIP REAL"
    )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] AIP original:"
    )

    print(
        AIP_PATH
    )

    print()

    print(
        "[OuroBuild] AIP temporário:"
    )

    print(
        temporary_aip
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
        "[OuroBuild] Versão:"
    )

    print(
        TEST_VERSION
    )

    print()

    print(
        "[OuroBuild] AIP original permaneceu intacto."
    )

    print(
        "=" * 80
    )