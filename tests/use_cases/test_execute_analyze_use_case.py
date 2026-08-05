"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_execute_analyze_use_case.py
Descrição : Testes do ExecuteAnalyzeUseCase.
--------------------------------------------------------------------
"""

from unittest.mock import Mock

from app.models.analyzers.analysis_result import (
    AnalysisResult,
)
from app.models.analyzers.analysis_status import (
    AnalysisStatus,
)
from app.models.analyzers.analyze_request import (
    AnalyzeRequest,
)
from app.use_cases.execute_analyze_use_case import (
    ExecuteAnalyzeUseCase,
)


def test_execute_should_update_project_metadata():
    """
    Deve executar a análise e atualizar a metadata do projeto.
    """

    #
    # Arrange
    #

    project_metadata_service = Mock()

    workspace_resolver = Mock()
    analysis_context_factory = Mock()
    project_reader = Mock()

    project_analyzer = Mock()
    framework_analyzer = Mock()
    build_analyzer = Mock()

    project_validator = Mock()

    request = AnalyzeRequest(
        project="ProjetoTeste",
        environment="DEV",
    )

    project_file = Mock()

    workspace_resolver.resolve_project.return_value = (
        project_file
    )

    context = Mock()

    context.project_file = project_file

    analysis_context_factory.create.return_value = (
        context
    )

    document = Mock()

    project_reader.read.return_value = (
        document
    )

    project = Mock()
    framework = Mock()
    build = Mock()

    project_analyzer.analyze.return_value = (
        project
    )

    framework_analyzer.analyze.return_value = (
        framework
    )

    build_analyzer.analyze.return_value = (
        build
    )

    project_validator.validate.return_value = []

    use_case = ExecuteAnalyzeUseCase(
        project_metadata_service=project_metadata_service,
        workspace_resolver=workspace_resolver,
        analysis_context_factory=analysis_context_factory,
        project_reader=project_reader,
        project_analyzer=project_analyzer,
        framework_analyzer=framework_analyzer,
        build_analyzer=build_analyzer,
        project_validator=project_validator,
    )

    #
    # Act
    #

    result = use_case.execute(
        request,
    )

    #
    # Assert
    #

    assert isinstance(
        result,
        AnalysisResult,
    )

    assert result.status == AnalysisStatus.SUCCESS

    workspace_resolver.resolve_project.assert_called_once()

    analysis_context_factory.create.assert_called_once()

    project_reader.read.assert_called_once()

    project_analyzer.analyze.assert_called_once()

    framework_analyzer.analyze.assert_called_once()

    build_analyzer.analyze.assert_called_once()

    project_validator.validate.assert_called_once()

    project_metadata_service.update_from_analysis.assert_called_once_with(
        project_id="ProjetoTeste",
        project_file=project_file,
    )