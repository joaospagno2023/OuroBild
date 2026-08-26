"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_disable_out_of_proc_build_service.py
Descrição : Testes do DisableOutOfProcBuildService.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.abstractions.process_service import (
    ProcessService,
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

from app.services.setup.disable_out_of_proc_build_service import (
    DisableOutOfProcBuildService,
)


def create_process_result() -> ProcessResult:
    """
    Cria um resultado mínimo de execução.
    """

    from datetime import datetime

    now = datetime.now()

    return ProcessResult(
        status=ProcessStatus.SUCCESS,
        exit_code=0,
        stdout="Success.",
        stderr="",
        duration=1.0,
        started_at=now,
        finished_at=now,
        executable=(
            "DisableOutOfProcBuild.exe"
        ),
        working_directory=(
            r"C:\VisualStudio"
        ),
        command_line=(
            "DisableOutOfProcBuild.exe"
        ),
    )


def create_service():
    """
    Cria o serviço com ProcessService falso.
    """

    process_service = MagicMock(
        spec=ProcessService,
    )

    process_service.execute.return_value = (
        create_process_result()
    )

    service = (
        DisableOutOfProcBuildService(
            process_service=process_service,
        )
    )

    return (
        service,
        process_service,
    )


def create_visual_studio(
    tmp_path: Path,
) -> Path:
    """
    Cria uma instalação fictícia do Visual Studio.
    """

    visual_studio_path = (
        tmp_path
        / "Microsoft Visual Studio"
        / "18"
        / "Professional"
        / "Common7"
        / "IDE"
        / "devenv.com"
    )

    visual_studio_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    visual_studio_path.write_text(
        "",
        encoding="utf-8",
    )

    disable_path = (
        visual_studio_path.parent
        / "CommonExtensions"
        / "Microsoft"
        / "VSI"
        / "DisableOutOfProcBuild"
        / "DisableOutOfProcBuild.exe"
    )

    disable_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    disable_path.write_text(
        "",
        encoding="utf-8",
    )

    return visual_studio_path


def test_deve_executar_disable_out_of_proc_build(
    tmp_path: Path,
):
    """
    Deve executar o utilitário do Visual Studio.
    """

    (
        service,
        process_service,
    ) = create_service()

    visual_studio_path = (
        create_visual_studio(
            tmp_path,
        )
    )

    result = service.execute(
        visual_studio_path,
    )

    assert result.status == ProcessStatus.SUCCESS

    assert result.exit_code == 0

    process_service.execute.assert_called_once()

    command = (
        process_service.execute.call_args.args[0]
    )

    assert isinstance(
        command,
        Command,
    )

    assert command.executable == (
        visual_studio_path.parent
        / "CommonExtensions"
        / "Microsoft"
        / "VSI"
        / "DisableOutOfProcBuild"
        / "DisableOutOfProcBuild.exe"
    )

    assert command.working_directory == (
        visual_studio_path.parent
    )

    assert command.arguments == []


def test_deve_rejeitar_visual_studio_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar o Visual Studio inexistente.
    """

    (
        service,
        process_service,
    ) = create_service()

    visual_studio_path = (
        tmp_path
        / "devenv.com"
    )

    with pytest.raises(
        FileNotFoundError,
        match="Executável do Visual Studio",
    ):
        service.execute(
            visual_studio_path,
        )

    process_service.execute.assert_not_called()


def test_deve_rejeitar_disable_out_of_proc_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar a instalação que não possui
    DisableOutOfProcBuild.exe.
    """

    (
        service,
        process_service,
    ) = create_service()

    visual_studio_path = (
        tmp_path
        / "Microsoft Visual Studio"
        / "18"
        / "Professional"
        / "Common7"
        / "IDE"
        / "devenv.com"
    )

    visual_studio_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    visual_studio_path.write_text(
        "",
        encoding="utf-8",
    )

    with pytest.raises(
        FileNotFoundError,
        match="DisableOutOfProcBuild.exe",
    ):
        service.execute(
            visual_studio_path,
        )

    process_service.execute.assert_not_called()