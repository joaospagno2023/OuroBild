"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_pipeline_runner_artifacts.py
Descrição : Testes de artefatos produzidos pela PipelineRunner.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import MagicMock

from app.models.pipeline.pipeline import (
    Pipeline,
)

from app.models.pipeline.pipeline_context import (
    PipelineContext,
)

from app.models.publish.publish_execution import (
    PublishExecution,
)

from app.pipeline.runner.pipeline_runner import (
    PipelineRunner,
)


def test_pipeline_runner_deve_identificar_pasta_de_publish(
    tmp_path: Path,
):
    """
    Deve identificar a pasta de saída informada
    pelo PublishExecution.
    """

    #
    # Arrange
    #

    output_folder = (
        tmp_path / "publish"
    )

    output_folder.mkdir()

    repository = MagicMock()

    runner = PipelineRunner(
        repository=repository,
    )

    #
    # Contexto
    #

    context = PipelineContext()

    #
    # PublishExecution
    #

    publish_execution = (
        PublishExecution()
    )

    publish_execution.summary.output_directory = (
        str(output_folder)
    )

    #
    # Pipeline
    #

    step = MagicMock()

    step.name = "Publish"

    pipeline = Pipeline(
        name="Teste Publish",
        steps=[step],
    )

    #
    # Mock do executor
    #

    runner._PipelineRunner__step_executor = (
        MagicMock()
    )

    runner._PipelineRunner__step_executor.execute.return_value = (
        MagicMock(
            name="Publish",
            status=MagicMock(),
            analysis=publish_execution,
            message="",
        )
    )

    #
    # Act
    #

    result = runner.execute(
        pipeline=pipeline,
        context=context,
    )

    #
    # Assert
    #

    assert result.publish is (
        publish_execution
    )


def test_pipeline_runner_deve_definir_output_folder(
    tmp_path: Path,
):
    """
    Deve definir a pasta de saída da Pipeline
    a partir do PublishExecution.
    """

    #
    # Arrange
    #

    output_folder = (
        tmp_path / "publish"
    )

    output_folder.mkdir()

    repository = MagicMock()

    runner = PipelineRunner(
        repository=repository,
    )

    context = PipelineContext()

    publish_execution = (
        PublishExecution()
    )

    publish_execution.summary.output_directory = (
        str(output_folder)
    )

    step = MagicMock()

    step.name = "Publish"

    pipeline = Pipeline(
        name="Teste Publish",
        steps=[step],
    )

    runner._PipelineRunner__step_executor = (
        MagicMock()
    )

    runner._PipelineRunner__step_executor.execute.return_value = (
        MagicMock(
            name="Publish",
            status=MagicMock(),
            analysis=publish_execution,
            message="",
        )
    )

    #
    # Act
    #

    result = runner.execute(
        pipeline=pipeline,
        context=context,
    )

    #
    # Assert
    #

    assert result.output_folder == (
        output_folder
    )


def test_pipeline_runner_deve_registrar_arquivos_do_publish(
    tmp_path: Path,
):
    """
    Deve registrar os arquivos existentes na pasta
    de saída do Publish como artefatos.
    """

    #
    # Arrange
    #

    output_folder = (
        tmp_path / "publish"
    )

    output_folder.mkdir()

    artifact_dll = (
        output_folder / "OuroNet.dll"
    )

    artifact_exe = (
        output_folder / "OuroNet.exe"
    )

    artifact_config = (
        output_folder / "Web.config"
    )

    artifact_dll.write_text(
        "dll",
        encoding="utf-8",
    )

    artifact_exe.write_text(
        "exe",
        encoding="utf-8",
    )

    artifact_config.write_text(
        "config",
        encoding="utf-8",
    )

    repository = MagicMock()

    runner = PipelineRunner(
        repository=repository,
    )

    context = PipelineContext()

    publish_execution = (
        PublishExecution()
    )

    publish_execution.summary.output_directory = (
        str(output_folder)
    )

    step = MagicMock()

    step.name = "Publish"

    pipeline = Pipeline(
        name="Teste Publish",
        steps=[step],
    )

    runner._PipelineRunner__step_executor = (
        MagicMock()
    )

    runner._PipelineRunner__step_executor.execute.return_value = (
        MagicMock(
            name="Publish",
            status=MagicMock(),
            analysis=publish_execution,
            message="",
        )
    )

    #
    # Act
    #

    result = runner.execute(
        pipeline=pipeline,
        context=context,
    )

    #
    # Assert
    #

    assert set(
        result.artifacts
    ) == {
        artifact_dll,
        artifact_exe,
        artifact_config,
    }


def test_pipeline_runner_nao_deve_considerar_subpastas_como_artefatos(
    tmp_path: Path,
):
    """
    Deve registrar somente arquivos diretamente existentes
    na pasta de Publish.
    """

    output_folder = (
        tmp_path / "publish"
    )

    output_folder.mkdir()

    artifact = (
        output_folder / "OuroNet.dll"
    )

    artifact.write_text(
        "dll",
        encoding="utf-8",
    )

    subfolder = (
        output_folder / "bin"
    )

    subfolder.mkdir()

    repository = MagicMock()

    runner = PipelineRunner(
        repository=repository,
    )

    context = PipelineContext()

    publish_execution = (
        PublishExecution()
    )

    publish_execution.summary.output_directory = (
        str(output_folder)
    )

    step = MagicMock()

    step.name = "Publish"

    pipeline = Pipeline(
        name="Teste Publish",
        steps=[step],
    )

    runner._PipelineRunner__step_executor = (
        MagicMock()
    )

    runner._PipelineRunner__step_executor.execute.return_value = (
        MagicMock(
            name="Publish",
            status=MagicMock(),
            analysis=publish_execution,
            message="",
        )
    )

    result = runner.execute(
        pipeline=pipeline,
        context=context,
    )

    assert result.artifacts == [
        artifact,
    ]