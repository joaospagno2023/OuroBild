"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : json_pipeline_execution_repository.py
Descrição : Implementação do repositório responsável por persistir
             execuções da Pipeline em arquivos JSON.
--------------------------------------------------------------------
"""

from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.abstractions.pipeline_execution_repository import (
    PipelineExecutionRepository,
)
from app.models.configuration.app_settings import (
    AppSettings,
)
from app.models.pipeline.pipeline_result import (
    PipelineResult,
)


class JsonPipelineExecutionRepository(
    PipelineExecutionRepository,
):
    """
    Repositório responsável por persistir execuções
    da Pipeline em arquivos JSON.
    """

    def __init__(
        self,
        settings: AppSettings,
    ) -> None:

        self.__settings = settings

    def save(
        self,
        result: PipelineResult,
    ) -> None:
        """
        Persiste uma execução da Pipeline.
        """

        execution_folder = (
            self.__create_execution_folder()
        )

        pipeline_file = (
            execution_folder /
            "pipeline.json"
        )

        pipeline_file.write_text(
            json.dumps(
                asdict(result),
                indent=4,
                ensure_ascii=False,
                default=str,
            ),
            encoding="utf-8",
        )

    def get_all(self) -> list[dict[str, Any]]:
        """
        Retorna todas as execuções persistidas.
        """

        executions: list[dict[str, Any]] = []

        if not self.__settings.executions_path.exists():
            return executions

        for pipeline_file in self.__settings.executions_path.glob(
            "*/pipeline.json"
        ):
            execution = self.__read_execution(
                pipeline_file,
            )

            if execution is not None:
                executions.append(execution)

        executions.sort(
            key=self.__sort_key,
            reverse=True,
        )

        return executions

    def get_by_execution_id(
        self,
        execution_id: str,
    ) -> dict[str, Any] | None:
        """
        Retorna uma execução pelo identificador.
        """

        if not self.__settings.executions_path.exists():
            return None

        for pipeline_file in self.__settings.executions_path.glob(
            "*/pipeline.json"
        ):
            execution = self.__read_execution(
                pipeline_file,
            )

            if execution is None:
                continue

            stored_execution_id = execution.get(
                "execution_id",
            )

            stored_session_id = execution.get(
                "session_id",
            )

            if (
                stored_execution_id == execution_id
                or (
                    not stored_execution_id
                    and stored_session_id == execution_id
                )
            ):
                return execution

        return None

    @staticmethod
    def __read_execution(
        pipeline_file: Path,
    ) -> dict[str, Any] | None:
        """
        Lê uma execução persistida.
        """

        try:
            return json.loads(
                pipeline_file.read_text(
                    encoding="utf-8",
                ),
            )
        except (
            OSError,
            json.JSONDecodeError,
        ):
            return None

    @staticmethod
    def __sort_key(
        execution: dict[str, Any],
    ) -> str:
        """
        Retorna uma chave estável para ordenar execuções.
        """

        started_at = execution.get(
            "started_at",
        )

        if isinstance(started_at, str):
            return started_at

        return ""

    def __create_execution_folder(
        self,
    ) -> Path:
        """
        Cria a pasta da execução.
        """

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S",
        )

        folder = (
            self.__settings.executions_path /
            f"{timestamp}_{uuid4().hex[:8].upper()}"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder
