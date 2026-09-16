"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_source_control_service.py
Descrição : Testes da política de hash/Get Last dos fontes.
--------------------------------------------------------------------
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from app.models.process.process_status import ProcessStatus
from app.models.source_control.project_source_state import ProjectSourceState
from app.services.source_control_service import SourceControlService


def test_nao_executa_get_last_quando_hash_nao_mudou(tmp_path: Path) -> None:
    source = tmp_path / "src"
    source.mkdir()
    (source / "Projeto.csproj").write_text("<Project />", encoding="utf-8")

    repository = MagicMock()
    current_hash = SourceControlService.calculate_source_hash(source)
    repository.get_by_project_id.return_value = ProjectSourceState(
        project_id="projeto",
        source_hash=current_hash,
    )

    process_service = MagicMock()
    service = SourceControlService(process_service, repository)

    executed, process, final_hash = service.synchronize("projeto", source)

    assert executed is False
    assert process is None
    assert final_hash == current_hash
    process_service.execute.assert_not_called()
    repository.save.assert_called_once()


def test_executa_get_last_quando_hash_mudou(tmp_path: Path) -> None:
    source = tmp_path / "src"
    source.mkdir()
    (source / "Projeto.csproj").write_text("<Project />", encoding="utf-8")

    repository = MagicMock()
    repository.get_by_project_id.return_value = ProjectSourceState(
        project_id="projeto",
        source_hash="hash-antigo",
        last_build_at=datetime(2026, 1, 1),
    )

    process_result = MagicMock()
    process_result.status = ProcessStatus.SUCCESS
    process_service = MagicMock()
    process_service.execute.return_value = process_result

    service = SourceControlService(process_service, repository)

    executed, process, final_hash = service.synchronize("projeto", source)

    assert executed is True
    assert process is process_result
    assert final_hash == SourceControlService.calculate_source_hash(source)
    process_service.execute.assert_called_once()
    command = process_service.execute.call_args.args[0]
    assert str(command.executable) == "tf.exe"
    assert [str(argument.value) for argument in command.arguments] == [
        "get",
        str(source.resolve()),
        "/recursive",
        "/noprompt",
    ]
    saved_state = repository.save.call_args.args[0]
    assert saved_state.source_hash == final_hash
    assert saved_state.last_get_last_at is not None
    assert saved_state.last_build_at == datetime(2026, 1, 1)
