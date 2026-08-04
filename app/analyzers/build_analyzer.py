"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_analyzer.py
Descrição : Responsável por analisar as informações de compilação.
--------------------------------------------------------------------
"""

from app.models.analyzers.build_profile import (
    BuildProfile,
)
from app.models.analyzers.project_document import (
    ProjectDocument,
)
from app.models.build.compilation_engine import (
    CompilationEngine,
)


class BuildAnalyzer:
    """
    Responsável por analisar as informações
    de compilação do projeto.
    """

    def analyze(
        self,
        document: ProjectDocument,
    ) -> BuildProfile:
        """
        Analisa as configurações de compilação.
        """

        output_type = document.get_property(
            "OutputType",
        )

        sign_assembly = (
            document.get_property(
                "SignAssembly",
            ).lower()
            == "true"
        )

        assembly_originator_key_file = (
            document.get_property(
                "AssemblyOriginatorKeyFile",
            )
        )

        compilation_engine = (
            self.__get_compilation_engine(
                document,
            )
        )

        return BuildProfile(

            compilation_engine=compilation_engine,

            output_type=output_type,

            sign_assembly=sign_assembly,

            assembly_originator_key_file=(
                assembly_originator_key_file
            ),
        )

    def __get_compilation_engine(
        self,
        document: ProjectDocument,
    ) -> CompilationEngine:
        """
        Determina o mecanismo de compilação
        do projeto.
        """

        if document.has_property(
            "TargetFramework",
        ):
            return CompilationEngine.DOTNET

        return CompilationEngine.MSBUILD