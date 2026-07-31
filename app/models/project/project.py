"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project.py
Descrição : Modelo que representa um projeto configurado para build.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class Project(BaseModel):
    """
    Representa um projeto configurado no arquivo projects.json.
    """

    id: str
    name: str
    description: str

    project_path: str
    aip_path: str
    publish_path: str

    output_msi: str
    network_path: str

    configuration: str
    platform: str

    enabled: bool