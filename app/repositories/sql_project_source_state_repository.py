"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_project_source_state_repository.py
Descrição : Repositório SQL Server do estado dos fontes.
--------------------------------------------------------------------
"""

from sqlalchemy import select

from app.abstractions.project_source_state_repository import ProjectSourceStateRepository
from app.database.connection import DatabaseConnection
from app.database.models.project_source_state_model import ProjectSourceStateModel
from app.models.source_control.project_source_state import ProjectSourceState


class SqlProjectSourceStateRepository(ProjectSourceStateRepository):
    """Persiste o estado dos fontes no SQL Server."""

    def __init__(self, database_connection: DatabaseConnection) -> None:
        if database_connection is None:
            raise ValueError("DatabaseConnection não foi informado.")
        self.__database_connection = database_connection

    def get_by_project_id(self, project_id: str) -> ProjectSourceState | None:
        if not project_id or not project_id.strip():
            raise ValueError("ProjectId não foi informado.")

        with self.__database_connection.create_session() as session:
            statement = select(ProjectSourceStateModel).where(
                ProjectSourceStateModel.project_id == project_id.strip()
            )
            model = session.scalars(statement).first()

            if model is None:
                return None

            return self.__to_domain(model)

    def save(self, state: ProjectSourceState) -> ProjectSourceState:
        if state is None:
            raise ValueError("ProjectSourceState não foi informado.")

        with self.__database_connection.create_session() as session:
            statement = select(ProjectSourceStateModel).where(
                ProjectSourceStateModel.project_id == state.project_id
            )
            model = session.scalars(statement).first()

            if model is None:
                model = ProjectSourceStateModel(
                    project_id=state.project_id,
                    source_hash=state.source_hash,
                    last_checked_at=state.last_checked_at,
                    last_get_last_at=state.last_get_last_at,
                    last_build_at=state.last_build_at,
                )
                session.add(model)
            else:
                model.source_hash = state.source_hash
                model.last_checked_at = state.last_checked_at
                model.last_get_last_at = state.last_get_last_at
                model.last_build_at = state.last_build_at

            session.flush()
            result = self.__to_domain(model)
            session.commit()
            return result

    @staticmethod
    def __to_domain(model: ProjectSourceStateModel) -> ProjectSourceState:
        return ProjectSourceState(
            project_id=model.project_id,
            source_hash=model.source_hash,
            last_checked_at=model.last_checked_at,
            last_get_last_at=model.last_get_last_at,
            last_build_at=model.last_build_at,
        )
