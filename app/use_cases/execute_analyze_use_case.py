"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execute_analyze_use_case.py
Descrição : Responsável por executar uma análise de projeto.
--------------------------------------------------------------------
"""

from app.analyzers.build_analyzer import (
    BuildAnalyzer,
)
from app.analyzers.framework_analyzer import (
    FrameworkAnalyzer,
)
from app.analyzers.project_analyzer import (
    ProjectAnalyzer,
)
from app.factories.analysis_context_factory import (
    AnalysisContextFactory,
)
from app.models.analyzers.analysis_result import (
    AnalysisResult,
)
from app.models.analyzers.analysis_status import (
    AnalysisStatus,
)
from app.models.analyzers.analyze_request import (
    AnalyzeRequest,
)
from app.models.analyzers.diagnostic import (
    Diagnostic,
)
from app.models.analyzers.severity import (
    Severity,
)
from app.readers.project_reader import (
    ProjectReader,
)
from app.validators.project_validator import (
    ProjectValidator,
)
from app.workspace.workspace_resolver import (
    WorkspaceResolver,
)

class ExecuteAnalyzeUseCase:
    """
    Responsável por executar a análise
    de um projeto.
    """

    def __init__(
        self,
        workspace_resolver: WorkspaceResolver,
        analysis_context_factory: AnalysisContextFactory,
        project_reader: ProjectReader,
        project_analyzer: ProjectAnalyzer,
        framework_analyzer: FrameworkAnalyzer,
        build_analyzer: BuildAnalyzer,
        project_validator: ProjectValidator,
    ) -> None:

        self.__analysis_context_factory = (
            analysis_context_factory
        )

        self.__project_reader = (
            project_reader
        )

        self.__project_analyzer = (
            project_analyzer
        )

        self.__framework_analyzer = (
            framework_analyzer
        )

        self.__build_analyzer = (
            build_analyzer
        )

        self.__project_validator = (
            project_validator
        )
        self.__workspace_resolver = (
            workspace_resolver
        )

    def execute(
        self,
        request: AnalyzeRequest,
    ) -> AnalysisResult:
        """
        Executa uma análise de projeto.
        """
        #
        # Resolve o projeto
        #

        project_file = (
            self.__workspace_resolver.resolve_project(
                project_id=request.project,
                environment_id=request.environment,
            )
        )
        #
        # Cria o contexto
        #

        resolved_project_file = (
            self.__workspace_resolver.resolve_project(
                project_id=request.project,
                environment_id=request.environment,
            )
        )

        context = (
            self.__analysis_context_factory.create(
                request=request,
                project_file=project_file,
            )
        )

        #
        # Carrega o projeto
        #

        document = (
            self.__project_reader.read(
                context.project_file,
            )
        )

        #
        # Executa os analyzers
        #

        project = (
            self.__project_analyzer.analyze(
                document,
            )
        )

        framework = (
            self.__framework_analyzer.analyze(
                document,
            )
        )

        build = (
            self.__build_analyzer.analyze(
                document,
            )
        )

        #
        # Executa os validators
        #

        diagnostics = []

        diagnostics.extend(
            self.__project_validator.validate(
                project,
            )
        )

        #
        # Calcula o status
        #

        status = self.__calculate_status(
            diagnostics,
        )

        #
        # Resultado
        #

        return AnalysisResult(

            status=status,

            project=project,

            framework=framework,

            build=build,

            diagnostics=diagnostics,

            recommendations=[],
        )

    def __calculate_status(
        self,
        diagnostics: list[Diagnostic],
    ) -> AnalysisStatus:
        """
        Calcula o status final da análise.
        """

        if any(
            diagnostic.severity == Severity.ERROR
            for diagnostic in diagnostics
        ):
            return AnalysisStatus.FAILED

        if any(
            diagnostic.severity == Severity.WARNING
            for diagnostic in diagnostics
        ):
            return AnalysisStatus.WARNING

        return AnalysisStatus.SUCCESS