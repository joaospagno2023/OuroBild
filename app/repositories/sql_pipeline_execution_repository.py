"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_pipeline_execution_repository.py
Descrição : Repositório SQL Server responsável pelo armazenamento
             das execuções da Pipeline.
--------------------------------------------------------------------
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select

from app.abstractions.pipeline_execution_repository import (
    PipelineExecutionRepository,
)
from app.database.connection import (
    DatabaseConnection,
)
from app.database.models.pipeline_execution_model import (
    PipelineExecutionModel,
)
from app.models.pipeline.pipeline_result import (
    PipelineResult,
)


class SqlPipelineExecutionRepository(PipelineExecutionRepository):
    """
    Implementação SQL Server do repositório de execuções da Pipeline.
    """

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        if database_connection is None:
            raise ValueError(
                "A conexão com o banco de dados é obrigatória."
            )

        self.__database_connection = database_connection

    def save(
        self,
        result: PipelineResult,
    ) -> None:
        """
        Salva ou atualiza uma execução da Pipeline.
        """
        if result is None:
            raise ValueError(
                "O resultado da execução é obrigatório."
            )

        if not result.execution_id:
            raise ValueError(
                "O execution_id é obrigatório."
            )

        if not result.project_id:
            raise ValueError(
                "O project_id é obrigatório."
            )

        model = PipelineExecutionModel(
            execution_id=result.execution_id,
            session_id=result.session_id,
            project_id=result.project_id,
            version=result.version,
            status=self.__get_status(result),
            success=result.success,
            message=result.message or None,
            failed_step=result.failed_step or None,
            started_at=result.started_at,
            finished_at=result.finished_at,
            elapsed_seconds=result.elapsed_seconds,
            output_folder=self.__get_output_folder(
                result.output_folder,
            ),
            artifacts_json=self.__serialize_paths(
                result.artifacts,
            ),
            steps_json=self.__serialize(result.steps),
            build_json=self.__serialize(result.build),
            publish_json=self.__serialize(result.publish),
            created_at=datetime.now(),
        )

        with self.__database_connection.create_session() as session:
            existing = session.scalar(
                select(PipelineExecutionModel).where(
                    PipelineExecutionModel.execution_id
                    == result.execution_id,
                )
            )

            if existing is not None:
                self.__update_model(
                    existing,
                    result,
                )
            else:
                session.add(model)

            session.commit()

    def get_all(self) -> list[dict[str, Any]]:
        """
        Retorna todas as execuções persistidas.
        """
        with self.__database_connection.create_session() as session:
            models = session.scalars(
                select(PipelineExecutionModel).order_by(
                    PipelineExecutionModel.started_at.desc()
                )
            ).all()

            return [
                self.__to_dict(model)
                for model in models
            ]

    def get_by_execution_id(
        self,
        execution_id: str,
    ) -> dict[str, Any] | None:
        """
        Retorna uma execução pelo identificador da execução.
        """
        if not execution_id:
            return None

        with self.__database_connection.create_session() as session:
            model = session.scalar(
                select(PipelineExecutionModel).where(
                    PipelineExecutionModel.execution_id
                    == execution_id,
                )
            )

            if model is None:
                return None

            return self.__to_dict(model)

    @staticmethod
    def __get_status(
        result: PipelineResult,
    ) -> str:
        """
        Determina o status atual da execução.

        Enquanto a execução ainda não possui FinishedAt, ela está
        em andamento. Após a finalização, o status depende do
        resultado da execução.
        """
        if result.finished_at is None:
            return "running"

        if result.success:
            return "completed"

        return "failed"

    @staticmethod
    def __get_output_folder(
        output_folder: Path | None,
    ) -> str | None:
        if output_folder is None:
            return None

        return str(output_folder)

    @staticmethod
    def __serialize(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        if hasattr(
            value,
            "__dataclass_fields__",
        ):
            value = asdict(value)

        elif isinstance(value, list):
            value = [
                asdict(item)
                if hasattr(
                    item,
                    "__dataclass_fields__",
                )
                else item
                for item in value
            ]

        try:
            return json.dumps(
                value,
                default=str,
                ensure_ascii=False,
            )
        except (TypeError, ValueError):
            return None

    @staticmethod
    def __serialize_paths(
        paths: list[Path],
    ) -> str | None:
        if not paths:
            return None

        return json.dumps(
            [str(path) for path in paths],
            ensure_ascii=False,
        )

    def __update_model(
        self,
        model: PipelineExecutionModel,
        result: PipelineResult,
    ) -> None:
        """
        Atualiza uma execução já persistida.
        """
        model.session_id = result.session_id
        model.project_id = result.project_id
        model.version = result.version
        model.status = self.__get_status(result)
        model.success = result.success
        model.message = result.message or None
        model.failed_step = result.failed_step or None
        model.started_at = result.started_at
        model.finished_at = result.finished_at
        model.elapsed_seconds = result.elapsed_seconds
        model.output_folder = self.__get_output_folder(
            result.output_folder,
        )
        model.artifacts_json = self.__serialize_paths(
            result.artifacts,
        )
        model.steps_json = self.__serialize(result.steps)
        model.build_json = self.__serialize(result.build)
        model.publish_json = self.__serialize(result.publish)

    @staticmethod
    def __to_dict(
        model: PipelineExecutionModel,
    ) -> dict[str, Any]:
        return {
            "execution_id": model.execution_id,
            "project_id": model.project_id,
            "session_id": model.session_id,
            "version": model.version,
            "success": model.success,
            "status": model.status,
            "message": model.message or "",
            "started_at": (
                model.started_at.isoformat()
                if model.started_at is not None
                else None
            ),
            "finished_at": (
                model.finished_at.isoformat()
                if model.finished_at is not None
                else None
            ),
            "elapsed_seconds": (
                float(model.elapsed_seconds)
                if model.elapsed_seconds is not None
                else 0.0
            ),
            "failed_step": model.failed_step,
            "output_folder": model.output_folder,
            "artifacts": (
                SqlPipelineExecutionRepository.__deserialize(
                    model.artifacts_json,
                )
            ),
            "steps": (
                SqlPipelineExecutionRepository.__deserialize(
                    model.steps_json,
                )
            ),
            "build": (
                SqlPipelineExecutionRepository.__deserialize(
                    model.build_json,
                )
            ),
            "publish": (
                SqlPipelineExecutionRepository.__deserialize(
                    model.publish_json,
                )
            ),
        }

    @staticmethod
    def __deserialize(
        value: str | None,
    ) -> Any:
        if not value:
            return None

        try:
            return json.loads(value)
        except (
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ):
            return None
