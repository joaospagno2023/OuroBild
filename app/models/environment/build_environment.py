"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_environment.py
Descrição : Representa um ambiente de Build.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel


class BuildEnvironment(BaseModel):
    """
    Representa um ambiente de Build.
    """

    id: str

    name: str

    resolver: str

    root_path: Path