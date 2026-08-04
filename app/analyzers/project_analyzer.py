"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_analyzer.py
Descrição : Responsável por analisar a identidade de um projeto.
--------------------------------------------------------------------
"""

from app.models.analyzers.project_document import (
    ProjectDocument,
)
from app.models.analyzers.project_profile import (
    ProjectProfile,
)


class ProjectAnalyzer:
    """
    Responsável por analisar as informações
    de identidade de um projeto.
    """

    def analyze(
        self,
        document: ProjectDocument,
    ) -> ProjectProfile:
        """
        Analisa um projeto e retorna
        seu perfil.
        """

        return ProjectProfile(

            name=document.file_path.stem,

            assembly_name=document.get_property(
                "AssemblyName",
            ),

            root_namespace=document.get_property(
                "RootNamespace",
            ),

            project_guid=document.get_property(
                "ProjectGuid",
            ),
        )