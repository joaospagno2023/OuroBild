"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_service.py
Descrição : Testes do AdvancedInstallerService.
--------------------------------------------------------------------
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.abstractions.process_service import (
    ProcessService,
)

from app.models.cleanup.cleanup_result import (
    CleanupResult,
)

from app.models.process.command import (
    Command,
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

from app.services.cleanup.build_artifact_cleanup_factory import (
    BuildArtifactCleanupFactory,
)
from app.services.cleanup.build_artifact_cleanup_service import (
    BuildArtifactCleanupService,
)

from app.services.setup.advanced_installer_aip_synchronizer import (
    AdvancedInstallerAipSynchronizer,
)

from app.services.setup.advanced_installer_service import (
    AdvancedInstallerService,
)


def create_process_result(
    status: ProcessStatus = ProcessStatus.SUCCESS,
    duration: float = 2.5,
    stderr: str = "",
) -> ProcessResult:
    """
    Cria um resultado mínimo de execução.
    """

    now = datetime.now()

    return ProcessResult(
        status=status,
        exit_code=(
            0
            if status == ProcessStatus.SUCCESS
            else 1
        ),
        stdout="Success.",
        stderr=stderr,
        duration=duration,
        started_at=now,
        finished_at=now,
        executable=(
            "AdvancedInstaller.com"
        ),
        working_directory=(
            r"C:\AdvancedInstaller"
        ),
        command_line=(
            "AdvancedInstaller.com"
        ),
    )


def create_service(
    tmp_path: Path,
):
    """
    Cria o serviço com dependências falsas.
    """

    process_service = MagicMock(
        spec=ProcessService,
    )

    process_service.execute.return_value = (
        create_process_result()
    )

    cleanup_service = MagicMock(
        spec=BuildArtifactCleanupService,
    )

    cleanup_service.execute.return_value = (
        CleanupResult(
            workspace_path=(
                tmp_path
                / "Publish"
            ),
            dry_run=False,
        )
    )

    advanced_installer_path = (
        tmp_path
        / "AdvancedInstaller.com"
    )

    advanced_installer_path.write_text(
        "",
        encoding="utf-8",
    )

    aip_synchronizer = MagicMock(
        spec=AdvancedInstallerAipSynchronizer,
    )

    cleanup_factory = MagicMock(
        spec=BuildArtifactCleanupFactory,
    )

    cleanup_factory.create.return_value = (
        cleanup_service
    )

    service = (
        AdvancedInstallerService(
            process_service=process_service,
            advanced_installer_path=(
                advanced_installer_path
            ),
            cleanup_factory=cleanup_factory,
            aip_synchronizer=aip_synchronizer,
        )
    )

    return (
        service,
        process_service,
        cleanup_service,
        advanced_installer_path,
        aip_synchronizer,
    )


def create_request() -> SetupRequest:
    """
    Cria uma solicitação de Setup.
    """

    return SetupRequest(
        project_id="teste",
        environment_id="teste",
    )


def create_definition(
    tmp_path: Path,
) -> SetupDefinition:
    """
    Cria uma definição de Setup.
    """

    solution_path = (
        tmp_path
        / "OuroNet.sln"
    )

    setup_project_path = (
        tmp_path
        / "OuroNet.aip"
    )

    solution_path.write_text(
        "",
        encoding="utf-8",
    )

    setup_project_path.write_text(
        "",
        encoding="utf-8",
    )

    return SetupDefinition(
        project_id="teste",
        name="OuroNet",
        product_name="OuroNet",
        manufacturer="Custom",
        version="1.0.0",
        configuration="Release",
        platform="x86",
        solution_path=solution_path,
        setup_project_path=setup_project_path,
        output_msi=(
            tmp_path
            / "OuroNet.msi"
        ),
    )


def create_paths(
    tmp_path: Path,
) -> SetupPaths:
    """
    Cria os caminhos utilizados pelo Setup.
    """

    aip_path = (
        tmp_path
        / "OuroNet.aip"
    )

    aip_path.write_text(
        "",
        encoding="utf-8",
    )

    output_msi = (
        tmp_path
        / "output"
        / "OuroNet.msi"
    )

    return SetupPaths(
        publish_path=(
            tmp_path
            / "Publish"
        ),
        setup_output_path=(
            tmp_path
            / "output"
        ),
        output_msi=output_msi,
        aip_path=aip_path,
    )


def test_deve_gerar_setup_com_sucesso(
    tmp_path: Path,
):
    """
    Deve gerar o Setup quando o RefreshSync
    e o Build terminarem com sucesso e o MSI existir.
    """

    (
        service,
        process_service,
        cleanup_service,
        advanced_installer_path,
        aip_synchronizer,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    paths = create_paths(
        tmp_path,
    )

    paths.output_msi.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths.output_msi.write_text(
        "MSI",
        encoding="utf-8",
    )

    process_service.execute.side_effect = [
        create_process_result(
            duration=2.5,
        ),
        create_process_result(
            duration=3.5,
        ),
    ]

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
        6.0
    )

    assert paths.output_msi.exists()

    assert (
        process_service.execute.call_count
        == 2
    )


def test_deve_executar_cleanup_antes_do_refresh_sync(
    tmp_path: Path,
):
    """
    Deve executar o Cleanup do Release antes
    do RefreshSync do Advanced Installer.
    """

    (
        service,
        process_service,
        cleanup_service,
        advanced_installer_path,
        aip_synchronizer,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    paths = create_paths(
        tmp_path,
    )

    paths.output_msi.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths.output_msi.write_text(
        "MSI",
        encoding="utf-8",
    )

    process_service.execute.side_effect = [
        create_process_result(
            duration=2.0,
        ),
        create_process_result(
            duration=3.0,
        ),
    ]

    service.install(
        request=create_request(),
        definition=definition,
        paths=paths,
    )

    cleanup_service.execute.assert_called_once_with(
        workspace_path=paths.publish_path,
        project_id="teste",
    )

    assert (
        process_service.execute.call_count
        == 2
    )


def test_deve_executar_refresh_sync_antes_do_build(
    tmp_path: Path,
):
    """
    Deve executar RefreshSync antes do Build.
    """

    (
        service,
        process_service,
        cleanup_service,
        advanced_installer_path,
        aip_synchronizer,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    paths = create_paths(
        tmp_path,
    )

    paths.output_msi.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths.output_msi.write_text(
        "MSI",
        encoding="utf-8",
    )

    process_service.execute.side_effect = [
        create_process_result(
            duration=2.0,
        ),
        create_process_result(
            duration=3.0,
        ),
    ]

    service.install(
        request=create_request(),
        definition=definition,
        paths=paths,
    )

    assert (
        process_service.execute.call_count
        == 2
    )

    first_command = (
        process_service
        .execute
        .call_args_list[0]
        .args[0]
    )

    second_command = (
        process_service
        .execute
        .call_args_list[1]
        .args[0]
    )

    assert isinstance(
        first_command,
        Command,
    )

    assert isinstance(
        second_command,
        Command,
    )

    first_arguments = [
        argument.value
        for argument in first_command.arguments
    ]

    second_arguments = [
        argument.value
        for argument in second_command.arguments
    ]

    workspace_aip_path = (
        paths.aip_path.parent
        / (paths.aip_path.stem + ".build.aip")
    )

    assert first_arguments == [
        "/edit",
        str(workspace_aip_path),
        "/RefreshSync",
    ]

    assert second_arguments == [
        "/build",
        str(workspace_aip_path),
    ]


def test_deve_montar_comando_refresh_sync_do_advanced_installer(
    tmp_path: Path,
):
    """
    Deve montar corretamente o comando
    de RefreshSync.
    """

    (
        service,
        process_service,
        cleanup_service,
        advanced_installer_path,
        aip_synchronizer,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    paths = create_paths(
        tmp_path,
    )

    paths.output_msi.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths.output_msi.write_text(
        "MSI",
        encoding="utf-8",
    )

    process_service.execute.side_effect = [
        create_process_result(),
        create_process_result(),
    ]

    service.install(
        request=create_request(),
        definition=definition,
        paths=paths,
    )

    command = (
        process_service
        .execute
        .call_args_list[0]
        .args[0]
    )

    assert isinstance(
        command,
        Command,
    )

    assert command.executable == (
        advanced_installer_path
    )

    assert command.working_directory == (
        paths.aip_path.parent
    )

    arguments = [
        argument.value
        for argument in command.arguments
    ]

    workspace_aip_path = (
        paths.aip_path.parent
        / (paths.aip_path.stem + ".build.aip")
    )

    assert arguments == [
        "/edit",
        str(workspace_aip_path),
        "/RefreshSync",
    ]


def test_deve_montar_comando_build_do_advanced_installer(
    tmp_path: Path,
):
    """
    Deve montar corretamente o comando
    de Build do Advanced Installer.
    """

    (
        service,
        process_service,
        cleanup_service,
        advanced_installer_path,
        aip_synchronizer,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    paths = create_paths(
        tmp_path,
    )

    paths.output_msi.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths.output_msi.write_text(
        "MSI",
        encoding="utf-8",
    )

    process_service.execute.side_effect = [
        create_process_result(),
        create_process_result(),
    ]

    service.install(
        request=create_request(),
        definition=definition,
        paths=paths,
    )

    command = (
        process_service
        .execute
        .call_args_list[1]
        .args[0]
    )

    assert isinstance(
        command,
        Command,
    )

    assert command.executable == (
        advanced_installer_path
    )

    assert command.working_directory == (
        paths.aip_path.parent
    )

    arguments = [
        argument.value
        for argument in command.arguments
    ]

    workspace_aip_path = (
        paths.aip_path.parent
        / (paths.aip_path.stem + ".build.aip")
    )

    assert arguments == [
        "/build",
        str(workspace_aip_path),
    ]


def test_deve_retornar_falha_quando_refresh_sync_falhar(
    tmp_path: Path,
):
    """
    Deve retornar falha quando o RefreshSync
    terminar com erro.
    """

    (
        service,
        process_service,
        cleanup_service,
        advanced_installer_path,
        aip_synchronizer,
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
            duration=2.5,
            stderr="Erro no RefreshSync.",
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

    assert result.duration_seconds == (
        2.5
    )

    assert "RefreshSync" in (
        result.message
    )

    assert "Erro no RefreshSync." in (
        result.message
    )

    process_service.execute.assert_called_once()


def test_deve_retornar_falha_quando_build_falhar(
    tmp_path: Path,
):
    """
    Deve retornar falha quando o Build
    terminar com erro.
    """

    (
        service,
        process_service,
        cleanup_service,
        advanced_installer_path,
        aip_synchronizer,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    paths = create_paths(
        tmp_path,
    )

    process_service.execute.side_effect = [
        create_process_result(
            status=ProcessStatus.SUCCESS,
            duration=2.5,
        ),
        create_process_result(
            status=ProcessStatus.FAILED,
            duration=3.5,
            stderr="Erro no Build.",
        ),
    ]

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

    assert result.duration_seconds == (
        6.0
    )

    assert "Build" in (
        result.message
    )

    assert "Erro no Build." in (
        result.message
    )

    assert (
        process_service.execute.call_count
        == 2
    )


def test_deve_retorna_falha_quando_msi_nao_for_gerado(
    tmp_path: Path,
):
    """
    Deve retornar falha quando RefreshSync e Build
    terminarem com sucesso, mas o MSI não existir.
    """

    (
        service,
        process_service,
        cleanup_service,
        advanced_installer_path,
        aip_synchronizer,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    paths = create_paths(
        tmp_path,
    )

    process_service.execute.side_effect = [
        create_process_result(
            duration=2.5,
        ),
        create_process_result(
            duration=3.5,
        ),
    ]

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
        "arquivo MSI não foi encontrado"
        in result.message
    )

    assert result.duration_seconds == (
        6.0
    )

    assert (
        process_service.execute.call_count
        == 2
    )


def test_deve_rejeitar_advanced_installer_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar o executável inexistente.
    """

    process_service = MagicMock(
        spec=ProcessService,
    )

    cleanup_service = MagicMock(
        spec=BuildArtifactCleanupService,
    )

    cleanup_factory = MagicMock(
        spec=BuildArtifactCleanupFactory,
    )

    cleanup_factory.create.return_value = (
        cleanup_service
    )

    aip_synchronizer = MagicMock(
        spec=AdvancedInstallerAipSynchronizer,
    )

    service = (
        AdvancedInstallerService(
            process_service=process_service,
            advanced_installer_path=(
                tmp_path
                / "AdvancedInstaller.com"
            ),
            cleanup_factory=cleanup_factory,
            aip_synchronizer=aip_synchronizer,
        )
    )

    definition = create_definition(
        tmp_path,
    )

    paths = create_paths(
        tmp_path,
    )

    with pytest.raises(
        FileNotFoundError,
        match="AdvancedInstaller.com",
    ):
        service.install(
            request=create_request(),
            definition=definition,
            paths=paths,
        )

    process_service.execute.assert_not_called()

    cleanup_service.execute.assert_not_called()


def test_deve_rejeitar_aip_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar o AIP inexistente.
    """

    (
        service,
        process_service,
        cleanup_service,
        advanced_installer_path,
        aip_synchronizer,
    ) = create_service(
        tmp_path,
    )

    definition = create_definition(
        tmp_path,
    )

    paths = SetupPaths(
        publish_path=(
            tmp_path
            / "Publish"
        ),
        setup_output_path=(
            tmp_path
            / "output"
        ),
        output_msi=(
            tmp_path
            / "output"
            / "OuroNet.msi"
        ),
        aip_path=(
            tmp_path
            / "AIP-Inexistente.aip"
        ),
    )

    with pytest.raises(
        FileNotFoundError,
        match="Arquivo AIP",
    ):
        service.install(
            request=create_request(),
            definition=definition,
            paths=paths,
        )

    process_service.execute.assert_not_called()

    cleanup_service.execute.assert_not_called()