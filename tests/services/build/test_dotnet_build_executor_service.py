"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_dotnet_build_executor_service.py
Descrição : Testes do DotnetBuildExecutorService.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import Mock
from unittest.mock import call

from app.models.build.build_context import (
    BuildContext,
)
from app.models.build.build_definition import (
    BuildDefinition,
)
from app.models.build.build_paths import (
    BuildPaths,
)
from app.models.process.process_result import (
    ProcessResult,
)
from app.models.process.process_status import (
    ProcessStatus,
)
from app.services.build.dotnet_build_executor_service import (
    DotnetBuildExecutorService,
)


def create_context() -> BuildContext:
    """
    Cria um contexto para os testes.
    """

    context = BuildContext(
        id="default",
        name="Default Build",
    )

    context.definition = BuildDefinition()

    context.paths = BuildPaths()

    context.paths.project_file = Path(
        r"C:\Projetos\TestProject\TestProject.csproj"
    )

    return context


def create_success_result() -> ProcessResult:
    """
    Cria um ProcessResult de sucesso.
    """

    return ProcessResult(
        status=ProcessStatus.SUCCESS,
        exit_code=0,
        stdout="OK",
        stderr="",
        duration=0.1,
    )


def create_failed_result() -> ProcessResult:
    """
    Cria um ProcessResult de erro.
    """

    return ProcessResult(
        status=ProcessStatus.FAILED,
        exit_code=1,
        stdout="",
        stderr="Erro",
        duration=0.1,
    )


def test_should_execute_restore_clean_build():
    """
    Deve executar:

    Restore
    Clean
    Build
    """

    #
    # Arrange
    #

    process = Mock()

    process.execute.side_effect = [
        create_success_result(),
        create_success_result(),
        create_success_result(),
    ]

    executor = DotnetBuildExecutorService(
        process_executor_service=process,
    )

    context = create_context()

    #
    # Act
    #

    result = executor.execute(
        context=context,
    )

    #
    # Assert
    #

    assert result.status == ProcessStatus.SUCCESS

    assert process.execute.call_count == 3

    expected_calls = [

        call(
            executable="dotnet",
            arguments=[
                "restore",
                str(context.paths.project_file),
                "--configuration",
                context.definition.configuration,
            ],
            working_directory=context.paths.project_file.parent,
        ),

        call(
            executable="dotnet",
            arguments=[
                "clean",
                str(context.paths.project_file),
                "--configuration",
                context.definition.configuration,
            ],
            working_directory=context.paths.project_file.parent,
        ),

        call(
            executable="dotnet",
            arguments=[
                "build",
                str(context.paths.project_file),
                "--configuration",
                context.definition.configuration,
                "--no-restore",
            ],
            working_directory=context.paths.project_file.parent,
        ),
    ]

    process.execute.assert_has_calls(
        expected_calls
    )


def test_should_stop_when_restore_fails():
    """
    Deve interromper a execução
    quando o Restore falhar.
    """

    #
    # Arrange
    #

    process = Mock()

    process.execute.return_value = (
        create_failed_result()
    )

    executor = DotnetBuildExecutorService(
        process_executor_service=process,
    )

    context = create_context()

    #
    # Act
    #

    result = executor.execute(
        context=context,
    )

    #
    # Assert
    #

    assert result.status == ProcessStatus.FAILED

    assert process.execute.call_count == 1


def test_should_stop_when_clean_fails():
    """
    Deve interromper a execução
    quando o Clean falhar.
    """

    #
    # Arrange
    #

    process = Mock()

    process.execute.side_effect = [
        create_success_result(),
        create_failed_result(),
    ]

    executor = DotnetBuildExecutorService(
        process_executor_service=process,
    )

    context = create_context()

    #
    # Act
    #

    result = executor.execute(
        context=context,
    )

    #
    # Assert
    #

    assert result.status == ProcessStatus.FAILED

    assert process.execute.call_count == 2