"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_publish_step.py
Descrição : Testes unitários da etapa de Publish via MSBuild.
--------------------------------------------------------------------
"""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.pipeline.pipeline_context import (
    PipelineContext,
)

from app.pipeline.steps.publish_step import (
    PublishStep,
)


def create_publish_context(
    tmp_path: Path,
):
    """
    Cria um contexto mínimo para os testes
    da PublishStep.
    """

    project_file = (
        tmp_path
        / "Projeto.csproj"
    )

    project_file.write_text(
        "<Project />",
        encoding="utf-8",
    )

    request = SimpleNamespace(
        configuration="Release",
        runtime=None,
        framework=None,
        output_directory=None,
        self_contained=False,
        publish_profile=None,
        single_file=False,
        ready_to_run=False,
        trimmed=False,
    )

    paths = SimpleNamespace(
        project_file=project_file,
    )

    publish_context = SimpleNamespace(
        request=request,
        paths=paths,
    )

    return PipelineContext(
        variables={
            "publish_context": publish_context,
        },
    )


def create_publish_step(
    process_service=None,
    msbuild_locator=None,
):
    """
    Cria a PublishStep para os testes.
    """

    if process_service is None:
        process_service = MagicMock()

    if msbuild_locator is None:
        msbuild_locator = MagicMock()

    return PublishStep(
        process_service=process_service,
        msbuild_locator=msbuild_locator,
    )


def test_publish_deve_possuir_nome_publish(
    tmp_path,
):
    """
    A Step deve possuir o nome Publish.
    """

    step = create_publish_step()

    assert step.name == "Publish"


def test_publish_deve_obter_msbuild_do_locator(
    tmp_path,
):
    """
    A Step deve utilizar o MSBuildLocator para
    descobrir o executável do MSBuild.
    """

    msbuild_path = Path(
        r"C:\Program Files\Microsoft Visual Studio\2022"
        r"\Enterprise\MSBuild\Current\Bin\MSBuild.exe"
    )

    locator = MagicMock()

    locator.get_msbuild_path.return_value = (
        msbuild_path
    )

    step = create_publish_step(
        msbuild_locator=locator,
    )

    context = create_publish_context(
        tmp_path,
    )

    executable = step.get_executable(
        context,
    )

    assert executable == msbuild_path

    locator.get_msbuild_path.assert_called_once()


def test_publish_deve_utilizar_diretorio_do_projeto(
    tmp_path,
):
    """
    O diretório de trabalho deve ser o diretório
    onde está localizado o projeto.
    """

    step = create_publish_step()

    context = create_publish_context(
        tmp_path,
    )

    working_directory = (
        step.get_working_directory(
            context,
        )
    )

    assert (
        working_directory
        == tmp_path
    )


def test_publish_deve_utilizar_target_publish(
    tmp_path,
):
    """
    O Publish deve utilizar o target /t:Publish.
    """

    step = create_publish_step()

    context = create_publish_context(
        tmp_path,
    )

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    assert (
        "/t:Publish"
        in values
    )


def test_publish_deve_informar_projeto(
    tmp_path,
):
    """
    O caminho do projeto deve ser enviado
    para o MSBuild.
    """

    step = create_publish_step()

    context = create_publish_context(
        tmp_path,
    )

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    assert str(
        tmp_path
        / "Projeto.csproj"
    ) in values


def test_publish_deve_informar_configuration(
    tmp_path,
):
    """
    A configuração deve ser enviada para
    o MSBuild.
    """

    step = create_publish_step()

    context = create_publish_context(
        tmp_path,
    )

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    assert (
        "/p:Configuration=Release"
        in values
    )


def test_publish_deve_informar_runtime(
    tmp_path,
):
    """
    Runtime deve ser enviado quando informado.
    """

    context = create_publish_context(
        tmp_path,
    )

    context.variables[
        "publish_context"
    ].request.runtime = (
        "win-x64"
    )

    step = create_publish_step()

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    assert (
        "/p:RuntimeIdentifier=win-x64"
        in values
    )


def test_publish_deve_informar_framework(
    tmp_path,
):
    """
    Framework deve ser enviado quando informado.
    """

    context = create_publish_context(
        tmp_path,
    )

    context.variables[
        "publish_context"
    ].request.framework = (
        "net8.0"
    )

    step = create_publish_step()

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    assert (
        "/p:TargetFramework=net8.0"
        in values
    )


def test_publish_deve_informar_pasta_saida(
    tmp_path,
):
    """
    A pasta de publicação deve ser enviada
    quando informada.
    """

    context = create_publish_context(
        tmp_path,
    )

    context.variables[
        "publish_context"
    ].request.output_directory = (
        "publish"
    )

    step = create_publish_step()

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    assert (
        "/p:PublishDir=publish"
        in values
    )


def test_publish_deve_informar_self_contained(
    tmp_path,
):
    """
    SelfContained deve ser enviado quando
    habilitado.
    """

    context = create_publish_context(
        tmp_path,
    )

    context.variables[
        "publish_context"
    ].request.self_contained = True

    step = create_publish_step()

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    assert (
        "/p:SelfContained=true"
        in values
    )


def test_publish_deve_informar_publish_profile(
    tmp_path,
):
    """
    PublishProfile deve ser enviado quando
    informado.
    """

    context = create_publish_context(
        tmp_path,
    )

    context.variables[
        "publish_context"
    ].request.publish_profile = (
        "Production"
    )

    step = create_publish_step()

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    assert (
        "/p:PublishProfile=Production"
        in values
    )


def test_publish_deve_informar_single_file(
    tmp_path,
):
    """
    PublishSingleFile deve ser enviado quando
    habilitado.
    """

    context = create_publish_context(
        tmp_path,
    )

    context.variables[
        "publish_context"
    ].request.single_file = True

    step = create_publish_step()

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    assert (
        "/p:PublishSingleFile=true"
        in values
    )


def test_publish_deve_informar_ready_to_run(
    tmp_path,
):
    """
    PublishReadyToRun deve ser enviado quando
    habilitado.
    """

    context = create_publish_context(
        tmp_path,
    )

    context.variables[
        "publish_context"
    ].request.ready_to_run = True

    step = create_publish_step()

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    assert (
        "/p:PublishReadyToRun=true"
        in values
    )


def test_publish_deve_informar_trimmed(
    tmp_path,
):
    """
    PublishTrimmed deve ser enviado quando
    habilitado.
    """

    context = create_publish_context(
        tmp_path,
    )

    context.variables[
        "publish_context"
    ].request.trimmed = True

    step = create_publish_step()

    arguments = step.get_arguments(
        context,
    )

    values = [
        argument.value
        for argument in arguments
    ]

    assert (
        "/p:PublishTrimmed=true"
        in values
    )