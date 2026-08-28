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

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.models.setup.setup_file_sync import (
    SetupFileSync,
)

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


def create_aip_with_msi_files(
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

<COMPONENT cid="caphyon.advinst.msicomp.MsiFilesComponent">
  <ROW
    File="ArquivoAntigo.dll"
    Component_="ArquivoAntigo.dll"
    SourcePath="ArquivoAntigo.dll"
  />
  <ROW
    File="ArquivoMantido.dll"
    Component_="ArquivoMantido.dll"
    SourcePath="ArquivoMantido.dll"
  />
</COMPONENT>
"""

    aip_path.write_text(
        content,
        encoding="utf-8",
    )

    return aip_path


def create_aip_with_msi_files_for_add(
    tmp_path: Path,
) -> Path:

    aip_path = (
        tmp_path
        / "TestAdd.aip"
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

<COMPONENT cid="caphyon.advinst.msicomp.MsiFilesComponent">
  <ROW
    File="ArquivoExistente.dll"
    Component_="ArquivoExistente.dll"
    SourcePath="ArquivoExistente.dll"
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


def test_deve_remover_arquivo_do_msi_files_component(
    tmp_path: Path,
):

    aip_path = create_aip_with_msi_files(
        tmp_path
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    change = SetupFileSync(
        name="ArquivoAntigo.dll",
        source_path="ArquivoAntigo.dll",
        publish_path=(
            publish_path
            / "ArquivoAntigo.dll"
        ),
        action=SetupFileAction.REMOVE,
    )

    modifier = (
        AdvancedInstallerAipModifier()
    )

    modifier.apply(
        aip_path=aip_path,
        version="10.7.8.0",
        publish_path=publish_path,
        changes=[
            change,
        ],
    )

    content = aip_path.read_text(
        encoding="utf-8",
    )

    assert (
        'File="ArquivoAntigo.dll"'
        not in content
    )

    assert (
        'File="ArquivoMantido.dll"'
        in content
    )

    assert (
        'SourcePath="ArquivoMantido.dll"'
        in content
    )


def test_deve_adicionar_arquivo_no_msi_files_component(
    tmp_path: Path,
):

    aip_path = create_aip_with_msi_files_for_add(
        tmp_path
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    change = SetupFileSync(
        name="ArquivoNovo.dll",
        source_path="ArquivoNovo.dll",
        publish_path=(
            publish_path
            / "ArquivoNovo.dll"
        ),
        action=SetupFileAction.ADD,
    )

    modifier = (
        AdvancedInstallerAipModifier()
    )

    modifier.apply(
        aip_path=aip_path,
        version="10.7.8.0",
        publish_path=publish_path,
        changes=[
            change,
        ],
    )

    content = aip_path.read_text(
        encoding="utf-8",
    )

    assert (
        'File="ArquivoNovo.dll"'
        in content
    )

    assert (
        'SourcePath="ArquivoNovo.dll"'
        in content
    )

    assert (
        'Component_="ArquivoNovo.dll"'
        in content
    )

    assert (
        'File="ArquivoExistente.dll"'
        in content
    )


def test_deve_rejeitar_adicao_de_arquivo_ja_existente(
    tmp_path: Path,
):

    aip_path = create_aip_with_msi_files_for_add(
        tmp_path
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    change = SetupFileSync(
        name="ArquivoExistente.dll",
        source_path="ArquivoExistente.dll",
        publish_path=(
            publish_path
            / "ArquivoExistente.dll"
        ),
        action=SetupFileAction.ADD,
    )

    modifier = (
        AdvancedInstallerAipModifier()
    )

    with pytest.raises(
        ValueError,
        match="já existe no AIP",
    ):

        modifier.apply(
            aip_path=aip_path,
            version="10.7.8.0",
            publish_path=publish_path,
            changes=[
                change,
            ],
        )


def test_deve_manter_arquivo_com_acao_keep(
    tmp_path: Path,
):

    aip_path = create_aip_with_msi_files(
        tmp_path
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    change = SetupFileSync(
        name="ArquivoMantido.dll",
        source_path="ArquivoMantido.dll",
        publish_path=(
            publish_path
            / "ArquivoMantido.dll"
        ),
        action=SetupFileAction.KEEP,
    )

    modifier = (
        AdvancedInstallerAipModifier()
    )

    modifier.apply(
        aip_path=aip_path,
        version="10.7.8.0",
        publish_path=publish_path,
        changes=[
            change,
        ],
    )

    content = aip_path.read_text(
        encoding="utf-8",
    )

    assert (
        'File="ArquivoMantido.dll"'
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