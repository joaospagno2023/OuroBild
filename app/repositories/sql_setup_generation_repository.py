"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_setup_generation_repository.py
Descrição : Repositório SQL Server responsável pelo armazenamento
             das gerações de Setup.
--------------------------------------------------------------------
"""

from datetime import datetime
from typing import Any

from sqlalchemy import select

from app.abstractions.setup_generation_repository import (
    SetupGenerationRepository,
)
from app.database.connection import DatabaseConnection
from app.database.models.setup_generation_file_model import (
    SetupGenerationFileModel,
)
from app.database.models.setup_generation_model import (
    SetupGenerationModel,
)


class SqlSetupGenerationRepository(SetupGenerationRepository):
    """
    Implementação SQL Server do repositório de gerações de Setup.
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

    def create_generation(
        self,
        generation_id: str,
        environment_id: str,
        version: str | None,
        revision: int | None,
        started_at: datetime,
        execution_id: str | None = None,
        validity_minutes: int = 5,
        created_by: str | None = None,
    ) -> None:
        if not generation_id:
            raise ValueError(
                "O generation_id é obrigatório."
            )

        if not environment_id:
            raise ValueError(
                "O environment_id é obrigatório."
            )

        if started_at is None:
            raise ValueError(
                "O started_at é obrigatório."
            )

        if validity_minutes <= 0:
            raise ValueError(
                "O validity_minutes deve ser maior que zero."
            )

        model = SetupGenerationModel(
            generation_id=generation_id,
            version=version,
            revision=revision,
            environment_id=environment_id,
            status="running",
            started_at=started_at,
            finished_at=None,
            last_file_path=None,
            last_file_generated_at=None,
            validity_minutes=validity_minutes,
            created_by=created_by,
            execution_id=execution_id,
        )

        with self.__database_connection.create_session() as session:
            existing = session.scalar(
                select(SetupGenerationModel).where(
                    SetupGenerationModel.generation_id
                    == generation_id,
                )
            )

            if existing is not None:
                raise ValueError(
                    f"A geração '{generation_id}' já está cadastrada."
                )

            session.add(model)
            session.commit()

    def finish_generation(
        self,
        generation_id: str,
        status: str,
        finished_at: datetime | None,
        last_file_path: str | None = None,
        last_file_generated_at: datetime | None = None,
    ) -> None:
        if not generation_id:
            raise ValueError(
                "O generation_id é obrigatório."
            )

        if not status:
            raise ValueError(
                "O status é obrigatório."
            )

        with self.__database_connection.create_session() as session:
            model = session.scalar(
                select(SetupGenerationModel).where(
                    SetupGenerationModel.generation_id
                    == generation_id,
                )
            )

            if model is None:
                raise ValueError(
                    f"A geração '{generation_id}' não foi encontrada."
                )

            model.status = status
            model.finished_at = finished_at

            if last_file_path is not None:
                model.last_file_path = last_file_path

            if last_file_generated_at is not None:
                model.last_file_generated_at = (
                    last_file_generated_at
                )

            session.commit()

    def register_file(
        self,
        generation_id: str,
        project_id: str,
        file_path: str,
        generated_at: datetime,
        success: bool,
    ) -> None:
        if not generation_id:
            raise ValueError(
                "O generation_id é obrigatório."
            )

        if not project_id:
            raise ValueError(
                "O project_id é obrigatório."
            )

        if not file_path:
            raise ValueError(
                "O file_path é obrigatório."
            )

        if generated_at is None:
            raise ValueError(
                "O generated_at é obrigatório."
            )

        with self.__database_connection.create_session() as session:
            generation_exists = session.scalar(
                select(SetupGenerationModel.generation_id).where(
                    SetupGenerationModel.generation_id
                    == generation_id,
                )
            )

            if generation_exists is None:
                raise ValueError(
                    f"A geração '{generation_id}' não foi encontrada."
                )

            model = SetupGenerationFileModel(
                generation_id=generation_id,
                project_id=project_id,
                file_path=file_path,
                generated_at=generated_at,
                success=success,
            )

            session.add(model)
            session.commit()

    def get_by_generation_id(
        self,
        generation_id: str,
    ) -> dict[str, Any] | None:
        if not generation_id:
            return None

        with self.__database_connection.create_session() as session:
            model = session.scalar(
                select(SetupGenerationModel).where(
                    SetupGenerationModel.generation_id
                    == generation_id,
                )
            )

            if model is None:
                return None

            return self.__to_generation_dict(model)

    def get_files(
        self,
        generation_id: str,
    ) -> list[dict[str, Any]]:
        if not generation_id:
            return []

        with self.__database_connection.create_session() as session:
            models = session.scalars(
                select(SetupGenerationFileModel)
                .where(
                    SetupGenerationFileModel.generation_id
                    == generation_id,
                )
                .order_by(
                    SetupGenerationFileModel.generated_at.asc()
                )
            ).all()

            return [
                self.__to_file_dict(model)
                for model in models
            ]

    def get_latest(
        self,
        environment_id: str,
        version: str | None,
        revision: int | None,
    ) -> dict[str, Any] | None:
        if not environment_id:
            return None

        with self.__database_connection.create_session() as session:
            statement = (
                select(SetupGenerationModel)
                .where(
                    SetupGenerationModel.environment_id
                    == environment_id,
                )
            )

            if version is None:
                statement = statement.where(
                    SetupGenerationModel.version.is_(None)
                )
            else:
                statement = statement.where(
                    SetupGenerationModel.version == version,
                )

            if revision is None:
                statement = statement.where(
                    SetupGenerationModel.revision.is_(None)
                )
            else:
                statement = statement.where(
                    SetupGenerationModel.revision == revision,
                )

            model = session.scalar(
                statement.order_by(
                    SetupGenerationModel.started_at.desc()
                )
            )

            if model is None:
                return None

            return self.__to_generation_dict(model)

    @staticmethod
    def __to_generation_dict(
        model: SetupGenerationModel,
    ) -> dict[str, Any]:
        return {
            "generation_id": model.generation_id,
            "version": model.version,
            "revision": model.revision,
            "environment_id": model.environment_id,
            "status": model.status,
            "started_at": model.started_at,
            "finished_at": model.finished_at,
            "last_file_path": model.last_file_path,
            "last_file_generated_at": model.last_file_generated_at,
            "validity_minutes": model.validity_minutes,
            "created_by": model.created_by,
            "execution_id": model.execution_id,
        }

    @staticmethod
    def __to_file_dict(
        model: SetupGenerationFileModel,
    ) -> dict[str, Any]:
        return {
            "id": model.id,
            "generation_id": model.generation_id,
            "project_id": model.project_id,
            "file_path": model.file_path,
            "generated_at": model.generated_at,
            "success": model.success,
        }