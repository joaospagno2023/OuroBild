"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_file.py
Descrição : Representa um arquivo utilizado pelo Setup Visual Studio.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel


class SetupFile(
    BaseModel,
):
    """
    Representa um arquivo que pertence ao Setup.
    """

    name: str

    source_path: str

    publish_path: Path

    assembly_display_name: str | None = None

    aip_file_id: str | None = None

    self_reg: bool = False