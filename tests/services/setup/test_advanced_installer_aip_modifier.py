"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_aip_modifier.py
Descrição : Testes do modificador de projetos
            Advanced Installer (.aip).
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.services.setup.advanced_installer_aip_modifier import (
    AdvancedInstallerAipModifier,
)


def create_aip(
    tmp_path: Path,
) -> Path:

    aip_path = (
        tmp_path
        / "Test.aip"
    )

    content = """
<COMPONENT cid="caphyon.advinst.msicomp.ProductDetailsComponent">
  <ROW
    Property="ProductVersion"
    Value="10.4.6.0"
    Options="32"
  />
</COMPONENT>

<COMPONENT cid="caphyon.advinst.msicomp.SynchronizedFolderComponent">
  <ROW
    Directory_="APPDIR"
    SourcePath="[SRC_BIN]"
    Feature="MainFeature"
  />
</COMPONENT>
"""

    aip_path.write_text(
        content,
        encoding="utf-8",
    )

    return aip_path


def test_deve_atualizar_versao_do_aip(
    tmp_path: Path,
):

    aip_path = create_aip(
        tmp_path
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    modifier = (
        AdvancedInstallerAipModifier()
    )

    modifier.apply(
        aip_path=aip_path,
        version="10.7.8.0",
        publish_path=publish_path,
    )

    content = aip_path.read_text(
        encoding="utf-8",
    )

    assert (
        'Property="ProductVersion"'
        in content
    )

    assert (
        'Value="10.7.8.0"'
        in content
    )


def test_deve_atualizar_source_path_da_pasta_sincronizada(
    tmp_path: Path,
):

    aip_path = create_aip(
        tmp_path
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    modifier = (
        AdvancedInstallerAipModifier()
    )

    modifier.apply(
        aip_path=aip_path,
        version="10.7.8.0",
        publish_path=publish_path,
    )

    content = aip_path.read_text(
        encoding="utf-8",
    )

    expected_path = (
        str(
            publish_path.resolve()
        )
        .replace(
            "\\",
            "\\\\",
        )
    )

    assert (
        f'SourcePath="{expected_path}"'
        in content
    )


def test_deve_manter_estrutura_da_pasta_sincronizada(
    tmp_path: Path,
):

    aip_path = create_aip(
        tmp_path
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    modifier = (
        AdvancedInstallerAipModifier()
    )

    modifier.apply(
        aip_path=aip_path,
        version="10.7.8.0",
        publish_path=publish_path,
    )

    content = aip_path.read_text(
        encoding="utf-8",
    )

    assert (
        "SynchronizedFolderComponent"
        in content
    )

    assert (
        'Directory_="APPDIR"'
        in content
    )

    assert (
        'Feature="MainFeature"'
        in content
    )


def test_deve_rejeitar_aip_inexistente(
    tmp_path: Path,
):

    aip_path = (
        tmp_path
        / "Inexistente.aip"
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    modifier = (
        AdvancedInstallerAipModifier()
    )

    with pytest.raises(
        FileNotFoundError,
        match="Arquivo AIP não encontrado",
    ):

        modifier.apply(
            aip_path=aip_path,
            version="10.7.8.0",
            publish_path=publish_path,
        )


def test_deve_rejeitar_publish_inexistente(
    tmp_path: Path,
):

    aip_path = create_aip(
        tmp_path
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    modifier = (
        AdvancedInstallerAipModifier()
    )

    with pytest.raises(
        FileNotFoundError,
        match="Pasta de publicação não encontrada",
    ):

        modifier.apply(
            aip_path=aip_path,
            version="10.7.8.0",
            publish_path=publish_path,
        )


def test_deve_rejeitar_versao_nao_informada(
    tmp_path: Path,
):

    aip_path = create_aip(
        tmp_path
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    modifier = (
        AdvancedInstallerAipModifier()
    )

    with pytest.raises(
        ValueError,
        match="A versão do AIP não foi informada",
    ):

        modifier.apply(
            aip_path=aip_path,
            version="",
            publish_path=publish_path,
        )


def test_deve_rejeitar_aip_sem_product_version(
    tmp_path: Path,
):

    aip_path = (
        tmp_path
        / "Test.aip"
    )

    aip_path.write_text(
        """
<COMPONENT>
  <ROW
    Property="CompanyName"
    Value="Custom"
  />
</COMPONENT>
""",
        encoding="utf-8",
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    modifier = (
        AdvancedInstallerAipModifier()
    )

    with pytest.raises(
        ValueError,
        match="ProductVersion",
    ):

        modifier.apply(
            aip_path=aip_path,
            version="10.7.8.0",
            publish_path=publish_path,
        )


def test_deve_rejeitar_aip_sem_pasta_sincronizada(
    tmp_path: Path,
):

    aip_path = (
        tmp_path
        / "Test.aip"
    )

    aip_path.write_text(
        """
<COMPONENT>
  <ROW
    Property="ProductVersion"
    Value="10.4.6.0"
  />
</COMPONENT>
""",
        encoding="utf-8",
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    modifier = (
        AdvancedInstallerAipModifier()
    )

    with pytest.raises(
        ValueError,
        match="pasta sincronizada",
    ):

        modifier.apply(
            aip_path=aip_path,
            version="10.7.8.0",
            publish_path=publish_path,
        )