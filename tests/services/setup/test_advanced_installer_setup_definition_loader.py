"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_setup_definition_loader.py
Descrição : Testes do loader de definição do Advanced Installer.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.models.setup.setup_definition import (
    SetupDefinition,
)

from app.services.setup.advanced_installer_setup_definition_loader import (
    AdvancedInstallerSetupDefinitionLoader,
)


def create_aip(
    tmp_path: Path,
) -> Path:
    """
    Cria um AIP mínimo válido para os testes.
    """

    aip_path = (
        tmp_path
        / "OuroNetWinServiceLinkPagamento.aip"
    )

    content = """
<ROW Property="Manufacturer" Value="Custom Software"/>
<ROW Property="ProductName" Value="OuroNetWinServiceLinkPagamento"/>
<ROW Property="ProductVersion" Value="10.4.6.0" Options="32"/>
"""

    aip_path.write_text(
        content.strip(),
        encoding="utf-8",
    )

    return aip_path


def test_deve_carregar_definicao_do_aip(
    tmp_path: Path,
):
    """
    Deve carregar as propriedades principais
    do AIP.
    """

    aip_path = create_aip(
        tmp_path,
    )

    loader = (
        AdvancedInstallerSetupDefinitionLoader()
    )

    output_msi = (
        tmp_path
        / "output"
        / "OuroNet.Setup.msi"
    )

    definition = loader.load(
        aip_path=aip_path,
        project_id="teste",
        configuration="Release",
        platform="x86",
        output_msi=output_msi,
    )

    assert isinstance(
        definition,
        SetupDefinition,
    )

    assert definition.project_id == (
        "teste"
    )

    assert definition.name == (
        "OuroNetWinServiceLinkPagamento"
    )

    assert definition.product_name == (
        "OuroNetWinServiceLinkPagamento"
    )

    assert definition.manufacturer == (
        "Custom Software"
    )

    assert definition.version == (
        "10.4.6.0"
    )

    assert definition.configuration == (
        "Release"
    )

    assert definition.platform == (
        "x86"
    )

    assert definition.setup_project_path == (
        aip_path
    )

    assert definition.output_msi == (
        output_msi
    )


def test_deve_rejeitar_aip_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar um AIP inexistente.
    """

    loader = (
        AdvancedInstallerSetupDefinitionLoader()
    )

    aip_path = (
        tmp_path
        / "inexistente.aip"
    )

    with pytest.raises(
        FileNotFoundError,
        match="Arquivo AIP não encontrado",
    ):
        loader.load(
            aip_path=aip_path,
            project_id="teste",
            configuration="Release",
            platform="x86",
            output_msi=(
                tmp_path
                / "output.msi"
            ),
        )


def test_deve_rejeitar_aip_que_nao_seja_arquivo(
    tmp_path: Path,
):
    """
    Deve rejeitar um caminho que represente
    um diretório.
    """

    aip_path = (
        tmp_path
        / "Projeto.aip"
    )

    aip_path.mkdir()

    loader = (
        AdvancedInstallerSetupDefinitionLoader()
    )

    with pytest.raises(
        ValueError,
        match="não é um arquivo",
    ):
        loader.load(
            aip_path=aip_path,
            project_id="teste",
            configuration="Release",
            platform="x86",
            output_msi=(
                tmp_path
                / "output.msi"
            ),
        )


def test_deve_rejeitar_product_name_ausente(
    tmp_path: Path,
):
    """
    Deve rejeitar AIP sem ProductName.
    """

    aip_path = (
        tmp_path
        / "Projeto.aip"
    )

    aip_path.write_text(
        """
<ROW Property="Manufacturer" Value="Custom Software"/>
<ROW Property="ProductVersion" Value="10.4.6.0"/>
""".strip(),
        encoding="utf-8",
    )

    loader = (
        AdvancedInstallerSetupDefinitionLoader()
    )

    with pytest.raises(
        ValueError,
        match="ProductName",
    ):
        loader.load(
            aip_path=aip_path,
            project_id="teste",
            configuration="Release",
            platform="x86",
            output_msi=(
                tmp_path
                / "output.msi"
            ),
        )


def test_deve_rejeitar_manufacturer_ausente(
    tmp_path: Path,
):
    """
    Deve rejeitar AIP sem Manufacturer.
    """

    aip_path = (
        tmp_path
        / "Projeto.aip"
    )

    aip_path.write_text(
        """
<ROW Property="ProductName" Value="OuroNet"/>
<ROW Property="ProductVersion" Value="10.4.6.0"/>
""".strip(),
        encoding="utf-8",
    )

    loader = (
        AdvancedInstallerSetupDefinitionLoader()
    )

    with pytest.raises(
        ValueError,
        match="Manufacturer",
    ):
        loader.load(
            aip_path=aip_path,
            project_id="teste",
            configuration="Release",
            platform="x86",
            output_msi=(
                tmp_path
                / "output.msi"
            ),
        )


def test_deve_rejeitar_product_version_ausente(
    tmp_path: Path,
):
    """
    Deve rejeitar AIP sem ProductVersion.
    """

    aip_path = (
        tmp_path
        / "Projeto.aip"
    )

    aip_path.write_text(
        """
<ROW Property="Manufacturer" Value="Custom Software"/>
<ROW Property="ProductName" Value="OuroNet"/>
""".strip(),
        encoding="utf-8",
    )

    loader = (
        AdvancedInstallerSetupDefinitionLoader()
    )

    with pytest.raises(
        ValueError,
        match="ProductVersion",
    ):
        loader.load(
            aip_path=aip_path,
            project_id="teste",
            configuration="Release",
            platform="x86",
            output_msi=(
                tmp_path
                / "output.msi"
            ),
        )