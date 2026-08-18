"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : inspect_vdproj_block.py
Descrição : Inspeciona um bloco real de arquivo .vdproj.
--------------------------------------------------------------------
"""

import sys

from pathlib import Path


PROJECT_ROOT = (
    Path(__file__).resolve().parents[1]
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)


vdproj_path = Path(
    r"C:\DvpLocal\WorkSpaceTFS\OuroNet\Scc\Producao\OuroNet"
    r"\04-Setup\OuroNet.Client.WinServiceLinkPagamento.Setup"
    r"\OuroNet.Client.WinServiceLinkPagamento.Setup.vdproj"
)


content = vdproj_path.read_text(
    encoding="utf-8",
)


parser = VdprojBlockParser()


block = parser.find_file_block(
    content=content,
    file_name="Custom.Framework.dll",
)


print(block.content)