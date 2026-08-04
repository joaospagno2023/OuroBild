"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_reader.py
Descrição : Responsável por carregar um arquivo .csproj.
--------------------------------------------------------------------
"""

from pathlib import Path
from xml.etree import ElementTree

from app.models.analyzers.project_document import (
    ProjectDocument,
)


class ProjectReader:
    """
    Responsável por carregar um arquivo .csproj.
    """

    def read(
        self,
        project_file: Path,
    ) -> ProjectDocument:

        tree = ElementTree.parse(
            project_file,
        )

        return ProjectDocument(

            file_path=project_file,

            root=tree.getroot(),
        )