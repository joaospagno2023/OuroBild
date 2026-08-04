"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_profile_analyzer.py
Descrição : Responsável por analisar a identidade de um projeto.
--------------------------------------------------------------------
"""

from xml.etree.ElementTree import (
    Element,
)

from app.models.analyzers.project_document import (
    ProjectDocument,
)
from app.models.analyzers.project_profile import (
    ProjectProfile,
)


class ProjectProfileAnalyzer:
    """
    Analisa as informações de identidade
    de um projeto.
    """

    def analyze(
        self,
        document: ProjectDocument,
    ) -> ProjectProfile:

        root = document.root

        return ProjectProfile(

            name=document.file_path.stem,

            assembly_name=self.__get_value(
                root,
                "AssemblyName",
            ),

            root_namespace=self.__get_value(
                root,
                "RootNamespace",
            ),

            project_guid=self.__get_value(
                root,
                "ProjectGuid",
            ),
        )

    def __get_value(
        self,
        root: Element,
        name: str,
    ) -> str:

        namespace = (
            "{http://schemas.microsoft.com/developer/msbuild/2003}"
        )

        element = root.find(
            f"{namespace}{name}",
        )

        if (
            element is None
            or element.text is None
        ):
            return ""

        return (
            element.text.strip()
        )