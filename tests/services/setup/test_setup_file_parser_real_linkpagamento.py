"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_file_parser_real_linkpagamento.py
Descrição : Valida o parser de arquivos no .vdproj real.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.services.setup.setup_file_parser import (
    SetupFileParser,
)


VDPROJ_PATH = Path(
    r"C:\DvpLocal\WorkSpaceTFS\OuroNet\Scc\Producao\OuroNet"
    r"\04-Setup\OuroNet.Client.WinServiceLinkPagamento.Setup"
    r"\OuroNet.Client.WinServiceLinkPagamento.Setup.vdproj"
)


PUBLISH_PATH = Path(
    r"C:\DvpLocal\WorkSpaceTFS\OuroNet\Scc\Producao\OuroNet"
    r"\02-Source\01-Client\OuroNet.Client.WinService.LinkPagamento"
    r"\bin\Release"
)


def test_deve_ler_dlls_do_setup_real():
    """
    Deve identificar as DLLs existentes no Setup real.
    """

    if not VDPROJ_PATH.exists():
        return

    content = VDPROJ_PATH.read_text(
        encoding="utf-8",
    )

    parser = SetupFileParser()

    result = parser.parse(
        content=content,
        publish_path=PUBLISH_PATH,
    )

    assert len(result) > 0

    names = {
        item.name
        for item in result
    }

    assert (
        "OuroNet.Client.WinService.Business.dll"
        in names
    )

    assert (
        "Custom.Framework.dll"
        in names
    )