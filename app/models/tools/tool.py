"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : tool.py
Descrição : Representa uma ferramenta instalada.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel

from app.models.tools.tool_name import (
    ToolName,
)


class Tool(
    BaseModel,
):
    """
    Representa uma ferramenta encontrada.
    """

    name: ToolName

    executable: Path

    version: str | None = None