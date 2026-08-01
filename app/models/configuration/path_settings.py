"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : path_settings.py
Descrição : Configurações de caminhos da aplicação.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class PathSettings(BaseModel):
    """
    Caminhos utilizados pela aplicação.
    """

    base_path: str

    installer_path: str

    publish_path: str