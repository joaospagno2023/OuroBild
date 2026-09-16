"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : source_control_service.py
Descrição : Calcula o hash dos fontes e executa o Get Last quando
             o estado dos fontes mudou desde o último processamento.
--------------------------------------------------------------------
"""

import hashlib
from datetime import datetime
from pathlib import Path

from app.abstractions.process_service import ProcessService
from app.abstractions.project_source_state_repository import ProjectSourceStateRepository
from app.models.process.command import Command
from app.models.process.command_argument import CommandArgument
from app.models.process.process_result import ProcessResult
from app.models.process.process_status import ProcessStatus
from app.models.source_control.project_source_state import ProjectSourceState
from app.utils.pipeline_logger import PipelineLogger


class SourceControlService:
    """Coordena hash dos fontes e Get Last do TFVC."""

    EXCLUDED_DIRECTORIES = {
        ".git",
        ".vs",
        ".svn",
        ".idea",
        "bin",
        "obj",
        "packages",
        "testresults",
        "coverage",
        "node_modules",
    }

    def __init__(
        self,
        process_service: ProcessService,
        repository: ProjectSourceStateRepository,
        tf_path: Path | None = None,
    ) -> None:
        if process_service is None:
            raise ValueError("ProcessService não foi informado.")
        if repository is None:
            raise ValueError("ProjectSourceStateRepository não foi informado.")
        self.__process_service = process_service
        self.__repository = repository
        self.__tf_path = Path(tf_path) if tf_path else Path("tf.exe")

    def synchronize(
        self,
        project_id: str,
        source_root: Path,
    ) -> tuple[bool, ProcessResult | None, str]:
        """Verifica alteração, executa Get Last quando necessário e salva o hash final."""

        if not project_id:
            raise ValueError("ProjectId não foi informado.")
        if source_root is None:
            raise ValueError("SourceRoot não foi informado.")

        source_root = Path(source_root).resolve()
        if not source_root.exists():
            raise ValueError(f"SourceRoot não encontrado: {source_root}")

        PipelineLogger.info("SOURCE CONTROL - CALCULANDO HASH DOS FONTES")
        current_hash = self.calculate_source_hash(source_root)
        PipelineLogger.info(f"SOURCE CONTROL - HASH ATUAL: {current_hash}")

        state = self.__repository.get_by_project_id(project_id)
        stored_hash = state.source_hash if state is not None else None

        PipelineLogger.info(
            "SOURCE CONTROL - HASH ARMAZENADO: "
            f"{stored_hash or '<nenhum>'}"
        )

        now = datetime.now()

        if state is not None and stored_hash == current_hash:
            state.last_checked_at = now
            self.__repository.save(state)
            PipelineLogger.info(
                "SOURCE CONTROL - NENHUMA ALTERAÇÃO DETECTADA. "
                "GET LAST NÃO SERÁ EXECUTADO."
            )
            return False, None, current_hash

        PipelineLogger.info(
            "SOURCE CONTROL - ALTERAÇÃO DETECTADA. EXECUTANDO GET LAST."
        )

        result = self.__get_last(source_root)

        if result.status != ProcessStatus.SUCCESS:
            PipelineLogger.error(
                "SOURCE CONTROL - GET LAST FALHOU. "
                f"ExitCode: {result.exit_code}"
            )
            return True, result, current_hash

        PipelineLogger.info("SOURCE CONTROL - GET LAST CONCLUÍDO COM SUCESSO.")

        final_hash = self.calculate_source_hash(source_root)
        PipelineLogger.info(
            f"SOURCE CONTROL - HASH APÓS GET LAST: {final_hash}"
        )

        updated_state = ProjectSourceState(
            project_id=project_id,
            source_hash=final_hash,
            last_checked_at=now,
            last_get_last_at=datetime.now(),
            last_build_at=(state.last_build_at if state else None),
        )
        self.__repository.save(updated_state)

        return True, result, final_hash

    def mark_build_success(self, project_id: str) -> None:
        """Registra no banco a data do último Build bem-sucedido."""

        state = self.__repository.get_by_project_id(project_id)
        if state is None:
            return
        state.last_build_at = datetime.now()
        self.__repository.save(state)

    @classmethod
    def calculate_source_hash(cls, source_root: Path) -> str:
        """Calcula SHA-256 determinístico dos arquivos de fonte."""

        root = Path(source_root).resolve()
        sha256 = hashlib.sha256()

        files = []
        for file in root.rglob("*"):
            if not file.is_file():
                continue
            if cls.__is_excluded(root, file):
                continue
            files.append(file)

        for file in sorted(files, key=lambda item: item.relative_to(root).as_posix().lower()):
            relative = file.relative_to(root).as_posix().lower()
            sha256.update(relative.encode("utf-8"))
            sha256.update(b"\0")

            with file.open("rb") as stream:
                while True:
                    chunk = stream.read(1024 * 1024)
                    if not chunk:
                        break
                    sha256.update(chunk)

            sha256.update(b"\0")

        return sha256.hexdigest()

    @classmethod
    def __is_excluded(cls, root: Path, file: Path) -> bool:
        try:
            relative_parts = file.relative_to(root).parts[:-1]
        except ValueError:
            return True

        return any(part.lower() in cls.EXCLUDED_DIRECTORIES for part in relative_parts)

    def __get_last(self, source_root: Path) -> ProcessResult:
        command = Command(
            executable=self.__tf_path,
            working_directory=source_root,
            arguments=[
                CommandArgument(value="get"),
                CommandArgument(value=str(source_root)),
                CommandArgument(value="/recursive"),
                CommandArgument(value="/noprompt"),
            ],
        )
        return self.__process_service.execute(command)
