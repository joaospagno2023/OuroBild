"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_history_service.py
Descrição : Serviço responsável por consultar o histórico de
             execuções persistidas.
--------------------------------------------------------------------
"""

from datetime import datetime
from typing import Any

from app.abstractions.pipeline_execution_repository import (
    PipelineExecutionRepository,
)
from app.abstractions.project_repository import (
    ProjectRepository,
)
from app.models.history.pipeline_history_detail import (
    PipelineHistoryDetail,
)
from app.models.history.pipeline_history_item import (
    PipelineHistoryItem,
)
from app.models.history.pipeline_history_logs import (
    PipelineHistoryLogs,
)
from app.utils.pipeline_logger import (
    PipelineLogger,
)


class PipelineHistoryService:
    """
    Consulta execuções persistidas e prepara os dados para a API.
    """

    def __init__(
        self,
        execution_repository: PipelineExecutionRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self.__execution_repository = execution_repository
        self.__project_repository = project_repository

    def get_all(self) -> list[PipelineHistoryItem]:
        """
        Retorna o histórico resumido.
        """
        executions = self.__execution_repository.get_all()

        return [
            self.__to_item(execution)
            for execution in executions
        ]

    def get_by_execution_id(
        self,
        execution_id: str,
    ) -> PipelineHistoryDetail | None:
        """
        Retorna os detalhes de uma execução.
        """
        execution = (
            self.__execution_repository.get_by_execution_id(
                execution_id,
            )
        )

        if execution is None:
            return None

        return self.__to_detail(execution)

    def get_logs(
        self,
        execution_id: str,
    ) -> PipelineHistoryLogs | None:
        """
        Retorna os logs associados a uma execução.
        """
        content = PipelineLogger.get_execution_log(
            execution_id,
        )

        if content is None:
            return None

        return PipelineHistoryLogs(
            execution_id=execution_id,
            content=content,
        )

    def __to_item(
        self,
        execution: dict[str, Any],
    ) -> PipelineHistoryItem:
        """
        Converte a execução persistida em item de histórico.
        """
        project_id = self.__get_string(
            execution.get("project_id"),
        )

        return PipelineHistoryItem(
            execution_id=self.__get_execution_id(execution),
            project_id=project_id,
            project_name=self.__get_project_name(project_id),
            session_id=self.__get_string(
                execution.get("session_id"),
            ),
            version=self.__get_optional_string(
                execution.get("version"),
            ),
            success=bool(
                execution.get("success", False),
            ),
            status=self.__get_status(
                execution,
            ),
            message=self.__get_string(
                execution.get("message"),
            ),
            started_at=self.__parse_datetime(
                execution.get("started_at"),
            ),
            finished_at=self.__parse_datetime(
                execution.get("finished_at"),
            ),
            elapsed_seconds=float(
                execution.get("elapsed_seconds", 0.0) or 0.0,
            ),
            failed_step=(
                self.__get_string(
                    execution.get("failed_step"),
                )
                or None
            ),
            steps_count=len(
                execution.get("steps") or [],
            ),
        )

    def __to_detail(
        self,
        execution: dict[str, Any],
    ) -> PipelineHistoryDetail:
        """
        Converte a execução persistida em detalhes de histórico.
        """
        item = self.__to_item(execution)

        artifacts = [
            self.__get_string(value)
            for value in execution.get("artifacts") or []
        ]

        output_folder = self.__get_string(
            execution.get("output_folder"),
        ) or None

        steps = execution.get("steps") or []
        build = execution.get("build")
        publish = execution.get("publish")

        return PipelineHistoryDetail(
            **item.model_dump(),
            output_folder=output_folder,
            artifacts=artifacts,
            steps=[
                value
                for value in steps
                if isinstance(value, dict)
            ],
            build=(
                build
                if isinstance(build, dict)
                else None
            ),
            publish=(
                publish
                if isinstance(publish, dict)
                else None
            ),
        )

    def __get_project_name(
        self,
        project_id: str,
    ) -> str:
        """
        Retorna o nome do projeto ou o identificador como fallback.
        """
        project = self.__project_repository.get_by_id(
            project_id,
        )

        if project is None:
            return project_id

        return project.name

    @staticmethod
    def __get_execution_id(
        execution: dict[str, Any],
    ) -> str:
        """
        Retorna o execution_id persistido.
        """
        execution_id = execution.get(
            "execution_id",
        )

        if isinstance(execution_id, str) and execution_id:
            return execution_id

        session_id = execution.get(
            "session_id",
        )

        if isinstance(session_id, str) and session_id:
            return session_id

        return ""

    @staticmethod
    def __get_string(
        value: object,
    ) -> str:
        """
        Converte um valor em texto de forma segura.
        """
        if value is None:
            return ""

        return str(value)

    @staticmethod
    def __get_optional_string(
        value: object,
    ) -> str | None:
        """
        Converte um valor opcional em texto.

        Retorna None quando o valor não foi informado ou quando
        o conteúdo textual está vazio.
        """
        if value is None:
            return None

        value_as_string = str(value).strip()

        if not value_as_string:
            return None

        return value_as_string

    @staticmethod
    def __get_status(
        execution: dict[str, Any],
    ) -> str:
        """
        Retorna o status persistido da execução.

        O campo Status do banco é a fonte principal. Para registros
        antigos sem Status, utiliza Success como fallback.
        """
        status = execution.get("status")

        if isinstance(status, str):
            normalized_status = status.strip().lower()

            if normalized_status in {
                "running",
                "completed",
                "failed",
            }:
                return normalized_status

        return (
            "completed"
            if bool(execution.get("success", False))
            else "failed"
        )

    @staticmethod
    def __parse_datetime(
        value: object,
    ) -> datetime | None:
        """
        Converte a representação textual da data persistida.
        """
        if isinstance(value, datetime):
            return value

        if not isinstance(value, str) or not value:
            return None

        try:
            return datetime.fromisoformat(
                value,
            )
        except ValueError:
            try:
                return datetime.strptime(
                    value,
                    "%Y-%m-%d %H:%M:%S.%f",
                )
            except ValueError:
                try:
                    return datetime.strptime(
                        value,
                        "%Y-%m-%d %H:%M:%S",
                    )
                except ValueError:
                    return None
