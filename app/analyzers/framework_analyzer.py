"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : framework_analyzer.py
Descrição : Responsável por analisar o framework de um projeto.
--------------------------------------------------------------------
"""

from app.models.analyzers.framework_profile import (
    FrameworkProfile,
)
from app.models.analyzers.project_document import (
    ProjectDocument,
)


class FrameworkAnalyzer:
    """
    Responsável por analisar o framework
    utilizado pelo projeto.
    """

    def analyze(
        self,
        document: ProjectDocument,
    ) -> FrameworkProfile:
        """
        Analisa o framework do projeto.
        """

        target_framework = document.get_property(
            "TargetFramework",
        )

        target_framework_version = (
            document.get_property(
                "TargetFrameworkVersion",
            )
        )

        tools_version = (
            document.get_property(
                "ToolsVersion",
            )
        )

        sdk_style = (
            target_framework != ""
        )

        return FrameworkProfile(

            target_framework=target_framework,

            target_framework_version=(
                target_framework_version
            ),

            sdk_style=sdk_style,

            tools_version=tools_version,
        )