"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_vdproj_setup_file_loader.py
Descrição : Testes do VdprojSetupFileLoader.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)

from app.services.setup.vdproj_setup_file_loader import (
    VdprojSetupFileLoader,
)


CONTENT = """
"FileSystem"
{
    "DefaultLocation" = "8:[ProgramFilesFolder][Manufacturer]\\[ProductName]"

    "{AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA}:_11111111111111111111111111111111"
    {
        "AssemblyRegister" = "3:1"
        "AssemblyIsInGAC" = "11:FALSE"
        "AssemblyAsmDisplayName" = "8:Existente, Version=10.4.7.0, Culture=neutral"

        "ScatterAssemblies"
        {
            "_111111"
            {
                "Name" = "8:Existente.dll"
                "Attributes" = "3:512"
            }
        }

        "SourcePath" = "8:Existente.dll"
        "TargetName" = "8:"
        "Tag" = "8:"
        "Folder" = "8:_AAAAAA"
        "Condition" = "8:"
        "Transitive" = "11:FALSE"
        "Vital" = "11:TRUE"
    }

    "{BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB}:_22222222222222222222222222222222"
    {
        "AssemblyRegister" = "3:1"
        "AssemblyIsInGAC" = "11:FALSE"
        "AssemblyAsmDisplayName" = "8:Outra, Version=10.4.7.0, Culture=neutral"

        "ScatterAssemblies"
        {
            "_222222"
            {
                "Name" = "8:Outra.dll"
                "Attributes" = "3:512"
            }
        }

        "SourcePath" = "8:Outra.dll"
        "TargetName" = "8:"
        "Tag" = "8:"
        "Folder" = "8:_BBBBBB"
        "Condition" = "8:"
        "Transitive" = "11:FALSE"
        "Vital" = "11:TRUE"
    }
}
"""


def create_project(
    tmp_path: Path,
) -> Path:
    """
    Cria um .vdproj temporário.
    """

    project = (
        tmp_path
        / "Setup.vdproj"
    )

    project.write_text(
        CONTENT,
        encoding="utf-8",
    )

    return project


def test_deve_carregar_arquivos_do_vdproj(
    tmp_path: Path,
):
    """
    Deve carregar os arquivos DLL existentes.
    """

    project = create_project(
        tmp_path,
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    loader = (
        VdprojSetupFileLoader(
            parser=(
                VdprojBlockParser()
            ),
        )
    )

    result = loader.load(
        setup_project_path=project,
        publish_path=publish_path,
    )

    assert len(result) == 2

    names = {
        item.name
        for item in result
    }

    assert names == {
        "Existente.dll",
        "Outra.dll",
    }


def test_deve_carregar_source_path(
    tmp_path: Path,
):
    """
    Deve preservar o SourcePath do .vdproj.
    """

    project = create_project(
        tmp_path,
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    loader = (
        VdprojSetupFileLoader(
            parser=(
                VdprojBlockParser()
            ),
        )
    )

    result = loader.load(
        setup_project_path=project,
        publish_path=publish_path,
    )

    existente = next(
        item
        for item in result
        if item.name
        == "Existente.dll"
    )

    assert (
        existente.source_path
        == "Existente.dll"
    )


def test_deve_carregar_assembly_display_name(
    tmp_path: Path,
):
    """
    Deve carregar o AssemblyAsmDisplayName.
    """

    project = create_project(
        tmp_path,
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    loader = (
        VdprojSetupFileLoader(
            parser=(
                VdprojBlockParser()
            ),
        )
    )

    result = loader.load(
        setup_project_path=project,
        publish_path=publish_path,
    )

    existente = next(
        item
        for item in result
        if item.name
        == "Existente.dll"
    )

    assert (
        existente.assembly_display_name
        == (
            "Existente, Version=10.4.7.0, "
            "Culture=neutral"
        )
    )


def test_deve_montar_publish_path(
    tmp_path: Path,
):
    """
    Deve montar o caminho físico no publish_path.
    """

    project = create_project(
        tmp_path,
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    loader = (
        VdprojSetupFileLoader(
            parser=(
                VdprojBlockParser()
            ),
        )
    )

    result = loader.load(
        setup_project_path=project,
        publish_path=publish_path,
    )

    existente = next(
        item
        for item in result
        if item.name
        == "Existente.dll"
    )

    assert (
        existente.publish_path
        == publish_path
        / "Existente.dll"
    )


def test_deve_rejeitar_setup_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar um .vdproj inexistente.
    """

    loader = (
        VdprojSetupFileLoader(
            parser=(
                VdprojBlockParser()
            ),
        )
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    try:
        loader.load(
            setup_project_path=(
                tmp_path
                / "NaoExiste.vdproj"
            ),
            publish_path=publish_path,
        )

        assert False

    except FileNotFoundError:
        assert True