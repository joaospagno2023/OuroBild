"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_vdproj_real_linkpagamento.py
Descrição : Valida o parser contra o .vdproj real do LinkPagamento.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)


VDPROJ_PATH = Path(
    r"C:\DvpLocal\WorkSpaceTFS\OuroNet\Scc\Producao\OuroNet"
    r"\04-Setup\OuroNet.Client.WinServiceLinkPagamento.Setup"
    r"\OuroNet.Client.WinServiceLinkPagamento.Setup.vdproj"
)


def test_deve_localizar_bloco_real_da_business():
    """
    Deve localizar o componente real da DLL Business.
    """

    if not VDPROJ_PATH.exists():
        return

    content = VDPROJ_PATH.read_text(
        encoding="utf-8",
    )

    parser = VdprojBlockParser()

    result = parser.find_file_block(
        content=content,
        file_name=(
            "OuroNet.Client.WinService.Business.dll"
        ),
    )

    assert (
        '"Name" = '
        '"8:OuroNet.Client.WinService.Business.dll"'
        in result.content
    )

    assert (
        '"SourcePath" = '
        '"8:OuroNet.Client.WinService.Business.dll"'
        in result.content
    )

    assert (
        '"AssemblyAsmDisplayName"'
        in result.content
    )

    assert (
        '"ScatterAssemblies"'
        in result.content
    )

    assert (
        '"Folder"'
        in result.content
    )


def test_deve_localizar_bloco_real_do_custom_framework():
    """
    Deve localizar o componente real da Custom.Framework.dll.
    """

    if not VDPROJ_PATH.exists():
        return

    content = VDPROJ_PATH.read_text(
        encoding="utf-8",
    )

    parser = VdprojBlockParser()

    result = parser.find_file_block(
        content=content,
        file_name="Custom.Framework.dll",
    )

    assert (
        '"Name" = "8:Custom.Framework.dll"'
        in result.content
    )

    assert (
        '"SourcePath" = "8:Custom.Framework.dll"'
        in result.content
    )

    assert (
        '"AssemblyAsmDisplayName"'
        in result.content
    )