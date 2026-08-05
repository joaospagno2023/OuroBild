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

from app.services.project_metadata_service import (
    ProjectMetadataService,
)

class ExecuteAnalyzeUseCase:
    """
    Responsável por executar a análise
    de um projeto.
    """

    def __init__(
        self,
        project_metadata_service: ProjectMetadataService,
        workspace_resolver: WorkspaceResolver,
        analysis_context_factory: AnalysisContextFactory,
        project_reader: ProjectReader,
        project_analyzer: ProjectAnalyzer,
        framework_analyzer: FrameworkAnalyzer,
        build_analyzer: BuildAnalyzer,
        project_validator: ProjectValidator,
    ) -> None:

        self.__project_metadata_service = (
            project_metadata_service
        )
        self.__workspace_resolver = (
            workspace_resolver
        )

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

        workspace = (
        self.__workspace_resolver.resolve(
                project_id=request.project,
                environment_id=request.environment,
            )
        )

        #
        # Cria o contexto
        #

        context = (
            self.__analysis_context_factory.create(
                request=request,
                project_file=workspace.project_file,
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

        diagnostics: list[Diagnostic] = []

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

        result = AnalysisResult(

            status=status,

            project=project,

            framework=framework,

            build=build,

            diagnostics=diagnostics,

            recommendations=[],
        )
        self.__project_metadata_service.update_from_analysis(
            project_id=request.project,
            project_file=context.project_file,
        )
        return result

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