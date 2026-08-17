"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_file.py
Descrição : Testes do SetupFile.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.setup.setup_file import (
    SetupFile,
)


def test_deve_criar_setup_file():
    """
    Deve criar um arquivo de Setup válido.
    """

    item = SetupFile(
        name="OuroNet.Client.WinService.Business.dll",
        source_path=(
            "OuroNet.Client.WinService.Business.dll"
        ),
        publish_path=Path(
            r"C:\Publish\OuroNet.Client.WinService.Business.dll"
        ),
        assembly_display_name=(
            "OuroNet.Client.WinService.Business, "
            "Version=10.4.7.0, "
            "Culture=neutral, "
            "PublicKeyToken=81568928c6d92f5f, "
            "processorArchitecture=MSIL"
        ),
    )

    assert item.name == (
        "OuroNet.Client.WinService.Business.dll"
    )

    assert item.source_path == (
        "OuroNet.Client.WinService.Business.dll"
    )

    assert item.publish_path == Path(
        r"C:\Publish\OuroNet.Client.WinService.Business.dll"
    )

    assert item.assembly_display_name is not None