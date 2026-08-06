"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_reader.py
Descrição : Responsável por carregar um arquivo .csproj.
--------------------------------------------------------------------
"""

from pathlib import Path
from xml.etree import ElementTree

from app.exceptions.invalid_project_file_exception import (
    InvalidProjectFileException,
)
from app.exceptions.project_file_not_found_exception import (
    ProjectNotFoundException,
)
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
        """
        Carrega um arquivo .csproj.
        """

        #
        # Verifica se o arquivo existe.
        #

        if not project_file.exists():

            raise ProjectFileNotFoundException(
                project_file=project_file,
            )

        #
        # Carrega o XML.
        #

        try:

            tree = ElementTree.parse(
                project_file,
            )

        except ElementTree.ParseError as ex:

            raise InvalidProjectFileException(
                project_file=project_file,
            ) from ex

        #
        # Retorna o documento.
        #

        return ProjectDocument(
            file_path=project_file,
            root=tree.getroot(),
        )