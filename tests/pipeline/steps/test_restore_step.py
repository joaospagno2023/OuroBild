"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_restore_step.py
Descrição : Testes unitários da RestoreStep.
--------------------------------------------------------------------
"""

from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.build.compilation_engine import (
    CompilationEngine,
)
from app.models.pipeline.pipeline_context import (
    PipelineContext,
)
from app.models.pipeline.step_status import (
    StepStatus,
)
from app.models.process.process_result import (
    ProcessResult,
)
from app.models.process.process_status import (
    ProcessStatus,
)
from app.pipeline.steps.restore_step import (
    RestoreStep,
)


def create_context(
    tmp_path: Path,
    engine: CompilationEngine = CompilationEngine.MSBUILD,
) -> PipelineContext:
    """
    Cria um PipelineContext mínimo para os testes.
    """

    project_file = (
        tmp_path / "Projeto.csproj"
    )

    project_file.write_text(
        "<Project />",
        encoding="utf-8",
    )

    project = SimpleNamespace(
        id="projeto",
        compilation_engine=engine,
        configuration="Release",
        platform="AnyCPU",
    )

    paths = SimpleNamespace(
        project_file=project_file,
        solution_file=None,
    )

    build_context = SimpleNamespace(
        project=project,
        paths=paths,
    )

    context = PipelineContext()

    context.variables["build_context"] = (
        build_context
    )

    return context


def create_process_result(
    status: ProcessStatus,
    stdout: str = "",
    stderr: str = "",
    exit_code: int = 0,
) -> ProcessResult:
    """
    Cria um ProcessResult válido para os testes.
    """

    started_at = datetime.now()

    finished_at = datetime.now()

    return ProcessResult(
        status=status,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        duration=1.0,
        started_at=started_at,
        finished_at=finished_at,
        executable="dotnet",
        working_directory=r"C:\Projetos",
        command_line=(
            "dotnet restore Projeto.csproj"
        ),
    )


def create_restore_step(
    metadata_service: MagicMock,
    process_service: MagicMock | None = None,
) -> RestoreStep:
    """
    Cria uma RestoreStep isolada para os testes.
    """

    if process_service is None:
        process_service = MagicMock()

    msbuild_locator = MagicMock()

    msbuild_locator.get_msbuild_path.return_value = (
        Path(
            r"C:\MSBuild\MSBuild.exe"
        )
    )

    return RestoreStep(
        process_service=process_service,
        msbuild_locator=msbuild_locator,
        project_metadata_service=metadata_service,
    )


def test_restore_deve_executar_quando_hash_for_diferente(
    tmp_path,
):
    """
    Quando o Restore for necessário,
    a regra deve indicar que a Step deve executar.
    """

    #
    # Arrange
    #

    metadata_service = MagicMock()

    metadata_service.is_restore_required.return_value = (
        True
    )

    context = create_context(
        tmp_path,
    )

    step = create_restore_step(
        metadata_service=metadata_service,
    )

    #
    # Act
    #

    result = step.should_execute(
        context,
    )

    #
    # Assert
    #

    assert result is True

    metadata_service.is_restore_required.assert_called_once()


def test_restore_deve_ser_skipped_quando_hash_for_igual(
    tmp_path,
):
    """
    Quando o Restore não for necessário, a Step deve
    retornar SKIPPED e não deve executar o processo.
    """

    #
    # Arrange
    #

    metadata_service = MagicMock()

    metadata_service.is_restore_required.return_value = (
        False
    )

    process_service = MagicMock()

    context = create_context(
        tmp_path,
    )

    step = create_restore_step(
        metadata_service=metadata_service,
        process_service=process_service,
    )

    #
    # Act
    #

    result = step.execute(
        context,
    )

    #
    # Assert
    #

    assert result.status == StepStatus.SKIPPED

    process_service.execute.assert_not_called()

    metadata_service.update_restore_hash.assert_not_called()


def test_restore_deve_executar_quando_hash_for_diferente(
    tmp_path,
):
    """
    Quando o Restore for necessário,
    o processo deve ser executado.
    """

    #
    # Arrange
    #

    metadata_service = MagicMock()

    metadata_service.is_restore_required.return_value = (
        True
    )

    process_service = MagicMock()

    process_service.execute.return_value = (
        create_process_result(
            status=ProcessStatus.SUCCESS,
            stdout="Restore concluído.",
        )
    )

    context = create_context(
        tmp_path,
    )

    step = create_restore_step(
        metadata_service=metadata_service,
        process_service=process_service,
    )

    #
    # Act
    #

    result = step.execute(
        context,
    )

    #
    # Assert
    #

    assert result.status == StepStatus.SUCCESS

    process_service.execute.assert_called_once()

    metadata_service.update_restore_hash.assert_called_once()


def test_restore_nao_deve_atualizar_hash_se_falhar(
    tmp_path,
):
    """
    Se o Restore falhar, o hash não deve ser atualizado.
    """

    #
    # Arrange
    #

    metadata_service = MagicMock()

    metadata_service.is_restore_required.return_value = (
        True
    )

    process_service = MagicMock()

    process_service.execute.return_value = (
        create_process_result(
            status=ProcessStatus.FAILED,
            stdout="",
            stderr="Erro no Restore.",
            exit_code=1,
        )
    )

    context = create_context(
        tmp_path,
    )

    step = create_restore_step(
        metadata_service=metadata_service,
        process_service=process_service,
    )

    #
    # Act
    #

    result = step.execute(
        context,
    )

    #
    # Assert
    #

    assert result.status == StepStatus.FAILED

    process_service.execute.assert_called_once()

    metadata_service.update_restore_hash.assert_not_called()


def test_restore_msbuild_deve_usar_msbuild(
    tmp_path,
):
    """
    Para MSBuild, o executável deve ser obtido
    através do MSBuildLocator.
    """

    #
    # Arrange
    #

    metadata_service = MagicMock()

    context = create_context(
        tmp_path,
        engine=CompilationEngine.MSBUILD,
    )

    msbuild_locator = MagicMock()

    msbuild_path = Path(
        r"C:\MSBuild\MSBuild.exe"
    )

    msbuild_locator.get_msbuild_path.return_value = (
        msbuild_path
    )

    step = RestoreStep(
        process_service=MagicMock(),
        msbuild_locator=msbuild_locator,
        project_metadata_service=metadata_service,
    )

    #
    # Act
    #

    executable = step.get_executable(
        context,
    )

    #
    # Assert
    #

    assert executable == msbuild_path

    msbuild_locator.get_msbuild_path.assert_called_once()


def test_restore_dotnet_deve_usar_dotnet(
    tmp_path,
):
    """
    Para o SDK .NET, o executável deve ser dotnet.
    """

    #
    # Arrange
    #

    metadata_service = MagicMock()

    context = create_context(
        tmp_path,
        engine=CompilationEngine.DOTNET,
    )

    step = create_restore_step(
        metadata_service=metadata_service,
    )

    #
    # Act
    #

    executable = step.get_executable(
        context,
    )

    #
    # Assert
    #

    assert executable == Path(
        "dotnet",
    )


def test_restore_msbuild_deve_montar_argumentos_corretamente(
    tmp_path,
):
    """
    Valida os argumentos do Restore utilizando MSBuild.
    """

    #
    # Arrange
    #

    metadata_service = MagicMock()

    context = create_context(
        tmp_path,
        engine=CompilationEngine.MSBUILD,
    )

    step = create_restore_step(
        metadata_service=metadata_service,
    )

    #
    # Act
    #

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    #
    # Assert
    #

    assert values == [
        str(
            context.variables[
                "build_context"
            ].paths.project_file
        ),
        "/t:Restore",
    ]


def test_restore_dotnet_deve_montar_argumentos_corretamente(
    tmp_path,
):
    """
    Valida os argumentos do Restore utilizando dotnet.
    """

    #
    # Arrange
    #

    metadata_service = MagicMock()

    context = create_context(
        tmp_path,
        engine=CompilationEngine.DOTNET,
    )

    step = create_restore_step(
        metadata_service=metadata_service,
    )

    #
    # Act
    #

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    #
    # Assert
    #

    assert values == [
        "restore",
        str(
            context.variables[
                "build_context"
            ].paths.project_file
        ),
    ]