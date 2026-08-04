"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : tool_settings.py
Descrição : Modelo de configuração de uma ferramenta.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class ToolSettings(BaseModel):
    """
    Representa a configuração de uma ferramenta.
    """

    path: str = ""

    auto_detect: bool = False