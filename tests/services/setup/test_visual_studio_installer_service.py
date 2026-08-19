"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_visual_studio_installer_service.py
Descrição : Testes do VisualStudioInstallerService.
--------------------------------------------------------------------
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.abstractions.process_service import (
    ProcessService,
)

from app.models.process.process_result import (
    ProcessResult,
)

from app.models.process.process_status import (
    ProcessStatus,
)

from app.models.setup.setup_definition import (
    SetupDefinition,
)

from app.models.setup.setup_paths import (
    SetupPaths,
)

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.models.setup.setup_result import (
    SetupResult,
)

from app.services.setup.visual_studio_installer_service import (
    VisualStudioInstallerService,
)

from app.services.setup.visual_studio_locator import (
    VisualStudioLocator,
)


def create_request() -> SetupRequest:
    """
    Cria uma solicitação mínima de Setup.
    """

    return SetupRequest(
        project_id="teste",
        environment_id="producao",
        version="1.0.0",
        revision=1,
        configuration="Release",
    )


def create_definition(
    tmp_path: Path,
) -> SetupDefinition:
    """
    Cria uma definição mínima de Setup.
    """

    solution_path = (
        tmp_path
        / "OuroNet.sln"
    )

    setup_project_path = (
        tmp_path
        / "Setup"
        / "OuroNet.Setup.vdproj"
    )

    solution_path.write_text(
        "",
        encoding="utf-8",
    )

    setup_project_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    setup_project_path.write_text(
        "",
        encoding="cp1252",
    )

    return SetupDefinition(
        project_id="teste",
        name="OuroNet.Setup",
        product_name="OuroNet",
        manufacturer="Custom Software",
        version="1.0.0",
        configuration="Release",
        platform="AnyCPU",
        solution_path=solution_path,
        setup_project_path=setup_project_path,
        output_msi=(
            tmp_path
            / "Release"
            / "OuroNet.msi"
        ),
    )


def create_paths(
    tmp_path: Path,
) -> SetupPaths:
    """
    Cria os caminhos mínimos necessários.
    """

    output_msi = (
        tmp_path
        / "Release"
        / "OuroNet.msi"
    )

    return SetupPaths(
        publish_path=(
            tmp_path
            / "publish"
        ),
        aip_path=(
            tmp_path
            / "Setup"
            / "OuroNet.Setup.vdproj"
        ),
        output_msi=output_msi,
        setup_output_path=(
            tmp_path
            / "Release"
        ),
    )


def create_process_result(
    status: ProcessStatus,
    exit_code: int = 0,
    stderr: str = "",
) -> ProcessResult:
    """
    Cria um ProcessResult para os testes.
    """

    now = datetime.now()

    return ProcessResult(
        status=status,
        exit_code=exit_code,
        stdout="Build realizado.",
        stderr=stderr,
        duration=2.5,
        started_at=now,
        finished_at=now,
        executable="devenv.com",
        working_directory=r"C:\Projetos",
        command_line="devenv.com ...",
    )


def create_service(
    tmp_path: Path,
):
    """
    Cria o serviço com ProcessService e
    VisualStudioLocator falsos.
    """

    process_service = MagicMock(
        spec=ProcessService,
    )

    visual_studio_locator = MagicMock(
        spec=VisualStudioLocator,
    )

    visual_studio_path = (
        tmp_path
        / "devenv.com"
    )

    visual_studio_path.write_text(
        "",
        encoding="utf-8",
    )

    visual_studio_locator.locate.return_value = (
        visual_studio_path
    )

    service = (
        VisualStudioInstallerService(
            process_service=process_service,
            visual_studio_locator=(
                visual_studio_locator
            ),
        )
    )

    return (
        service,
        process_service,
        visual_studio_locator,
    )


def test_deve_gerar_setup_com_sucesso(
    tmp_path: Path,
):
    """
    Deve gerar o Setup quando o processo
    terminar com sucesso e o MSI intermediário
    existir.

    O MSI intermediário é gerado no diretório
    Release do projeto Setup e depois copiado
    para paths.output_msi.
    """

    (
        service,
        process_service,
        visual_studio_locator,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    paths = create_paths(
        tmp_path,
    )

    #
    # Caminho onde o Visual Studio deve gerar
    # o MSI intermediário.
    #

    intermediate_msi = (
        definition.setup_project_path.parent
        / definition.configuration
        / (
            f"{definition.setup_project_path.stem}"
            ".msi"
        )
    )

    intermediate_msi.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    intermediate_msi.write_text(
        "MSI",
        encoding="utf-8",
    )

    process_service.execute.return_value = (
        create_process_result(
            status=ProcessStatus.SUCCESS,
        )
    )

    result = service.install(
        request=create_request(),
        definition=definition,
        paths=paths,
    )

    assert isinstance(
        result,
        SetupResult,
    )

    assert result.success is True

    assert result.project_id == (
        "teste"
    )

    assert result.output_msi == (
        paths.output_msi
    )

    assert result.duration_seconds == (
        2.5
    )

    assert paths.output_msi.exists()

    assert paths.output_msi.read_text(
        encoding="utf-8",
    ) == "MSI"

    #
    # O MSI intermediário deve ter sido
    # removido depois da cópia.
    #

    assert not intermediate_msi.exists()

    visual_studio_locator.locate.assert_called_once()

    process_service.execute.assert_called_once()


def test_deve_montar_comando_visual_studio(
    tmp_path: Path,
):
    """
    Deve montar corretamente o comando
    utilizado pelo Visual Studio.
    """

    (
        service,
        process_service,
        visual_studio_locator,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    paths = create_paths(
        tmp_path,
    )

    #
    # Cria o MSI intermediário para que o
    # serviço possa concluir normalmente.
    #

    intermediate_msi = (
        definition.setup_project_path.parent
        / definition.configuration
        / (
            f"{definition.setup_project_path.stem}"
            ".msi"
        )
    )

    intermediate_msi.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    intermediate_msi.write_text(
        "MSI",
        encoding="utf-8",
    )

    process_service.execute.return_value = (
        create_process_result(
            status=ProcessStatus.SUCCESS,
        )
    )

    service.install(
        request=create_request(),
        definition=definition,
        paths=paths,
    )

    visual_studio_locator.locate.assert_called_once()

    command = (
        process_service.execute.call_args.args[0]
    )

    expected_visual_studio_path = (
        visual_studio_locator.locate.return_value
    )

    assert command.executable == (
        expected_visual_studio_path
    )

    assert command.working_directory == (
        definition.solution_path.parent
    )

    arguments = [
        argument.value
        for argument in command.arguments
    ]

    assert arguments == [
        str(
            definition.solution_path,
        ),
        "/Build",
        "Release",
        "/Project",
        definition.setup_project_path.stem,
        "/ProjectConfig",
        "Release",
    ]


def test_deve_retornar_falha_quando_visual_studio_falhar(
    tmp_path: Path,
):
    """
    Deve retornar falha quando o Visual Studio
    terminar com erro.
    """

    (
        service,
        process_service,
        visual_studio_locator,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    paths = create_paths(
        tmp_path,
    )

    process_service.execute.return_value = (
        create_process_result(
            status=ProcessStatus.FAILED,
            exit_code=1,
            stderr="Erro ao gerar Setup.",
        )
    )

    result = service.install(
        request=create_request(),
        definition=definition,
        paths=paths,
    )

    assert result.success is False

    assert result.project_id == (
        "teste"
    )

    assert result.output_msi is None

    assert "Falha ao gerar o Setup" in (
        result.message
    )

    assert "Erro ao gerar Setup." in (
        result.message
    )


def test_deve_rejeitar_solution_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar uma solução inexistente.
    """

    (
        service,
        process_service,
        visual_studio_locator,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    definition.solution_path.unlink()

    paths = create_paths(
        tmp_path,
    )

    with pytest.raises(
        FileNotFoundError,
        match="solução do Setup",
    ):
        service.install(
            request=create_request(),
            definition=definition,
            paths=paths,
        )

    visual_studio_locator.locate.assert_not_called()

    process_service.execute.assert_not_called()


def test_deve_rejeitar_projeto_setup_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar um projeto de Setup inexistente.
    """

    (
        service,
        process_service,
        visual_studio_locator,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    definition.setup_project_path.unlink()

    paths = create_paths(
        tmp_path,
    )

    with pytest.raises(
        FileNotFoundError,
        match="projeto de Setup",
    ):
        service.install(
            request=create_request(),
            definition=definition,
            paths=paths,
        )

    visual_studio_locator.locate.assert_not_called()

    process_service.execute.assert_not_called()


def test_deve_retorna_falha_quando_msi_nao_for_gerado(
    tmp_path: Path,
):
    """
    Deve retornar falha quando o Visual Studio
    terminar com sucesso, mas não gerar o MSI.
    """

    (
        service,
        process_service,
        visual_studio_locator,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    paths = create_paths(
        tmp_path,
    )

    process_service.execute.return_value = (
        create_process_result(
            status=ProcessStatus.SUCCESS,
        )
    )

    result = service.install(
        request=create_request(),
        definition=definition,
        paths=paths,
    )

    assert result.success is False

    assert result.project_id == (
        "teste"
    )

    assert result.output_msi is None

    assert (
        "MSI intermediário não foi encontrado"
        in result.message
    )

    visual_studio_locator.locate.assert_called_once()