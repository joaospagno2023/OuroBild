"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_document.py
Descrição : Representa um projeto MSBuild carregado em memória.
--------------------------------------------------------------------
"""

from pathlib import Path
from xml.etree.ElementTree import Element


class ProjectDocument:
    """
    Representa um arquivo .csproj carregado.
    """

    def __init__(
        self,
        file_path: Path,
        root: Element,
    ) -> None:

        self.file_path = file_path

        self.root = root