"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : analyze_project_use_case.py
Descrição : Caso de uso responsável por analisar um projeto.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.analyzers.build_analyzer import (
    BuildAnalyzer,
)
from app.analyzers.framework_analyzer import (
    FrameworkAnalyzer,
)
from app.analyzers.project_analyzer import (
    ProjectAnalyzer,
)
from app.models.analyzers.analysis_result import (
    AnalysisResult,
)
from app.models.analyzers.analysis_status import (
    AnalysisStatus,
)
from app.readers.project_reader import (
    ProjectReader,
)


class AnalyzeProjectUseCase:
    """
    Caso de uso responsável pela análise
    de um projeto.
    """

    def __init__(
        self,
        project_reader: ProjectReader,
        project_analyzer: ProjectAnalyzer,
        framework_analyzer: FrameworkAnalyzer,
        build_analyzer: BuildAnalyzer,
    ) -> None:

        self.__project_reader = project_reader
        self.__project_analyzer = project_analyzer
        self.__framework_analyzer = framework_analyzer
        self.__build_analyzer = build_analyzer

    def execute(
        self,
        project_file: Path,
    ) -> AnalysisResult:
        """
        Executa a análise de um projeto.
        """

        document = self.__project_reader.read(
            project_file,
        )

        project = self.__project_analyzer.analyze(
            document,
        )

        framework = (
            self.__framework_analyzer.analyze(
                document,
            )
        )

        build = self.__build_analyzer.analyze(
            document,
        )

        return AnalysisResult(

            status=AnalysisStatus.SUCCESS,

            project=project,

            framework=framework,

            build=build,
        )