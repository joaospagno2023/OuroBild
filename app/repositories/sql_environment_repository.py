"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_environment_repository.py
Descrição : Repositório de ambientes utilizando SQL Server.
--------------------------------------------------------------------
"""

from pathlib import Path

from sqlalchemy import select

from app.abstractions.environment_repository import (
    EnvironmentRepository,
)
from app.database.connection import (
    DatabaseConnection,
)
from app.database.models.environment_model import (
    EnvironmentModel,
)
from app.models.environment.build_environment import (
    BuildEnvironment,
)


class SqlEnvironmentRepository(
    EnvironmentRepository,
):
    """
    Implementação do repositório de ambientes para SQL Server.
    """

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        """
        Inicializa o repositório.
        """

        if database_connection is None:
            raise ValueError(
                "DatabaseConnection não foi informado."
            )

        self.__database_connection = (
            database_connection
        )

    def get_all(
        self,
    ) -> list[BuildEnvironment]:
        """
        Retorna todos os ambientes ordenados pelo identificador.
        """

        with self.__database_connection.create_session() as session:
            statement = (
                select(EnvironmentModel)
                .order_by(
                    EnvironmentModel.id,
                )
            )

            environment_models = (
                session.scalars(
                    statement,
                )
                .all()
            )

            return [
                self.__to_environment(
                    environment_model,
                )
                for environment_model in environment_models
            ]

    def get_by_id(
        self,
        environment_id: str,
    ) -> BuildEnvironment | None:
        """
        Localiza um ambiente pelo identificador.
        """

        if not environment_id:
            raise ValueError(
                "EnvironmentId não foi informado."
            )

        with self.__database_connection.create_session() as session:
            statement = (
                select(EnvironmentModel)
                .where(
                    EnvironmentModel.id == environment_id,
                )
            )

            environment_model = (
                session.scalars(
                    statement,
                )
                .first()
            )

            if environment_model is None:
                return None

            return self.__to_environment(
                environment_model,
            )

    def create(
        self,
        environment: BuildEnvironment,
    ) -> BuildEnvironment:
        """
        Cria um ambiente.
        """

        if environment is None:
            raise ValueError(
                "BuildEnvironment não foi informado."
            )

        with self.__database_connection.create_session() as session:
            environment_model = EnvironmentModel(
                id=environment.id,
                name=environment.name,
                resolver=environment.resolver,
                root_path=str(
                    environment.root_path,
                ),
            )

            session.add(
                environment_model,
            )

            session.commit()

            return self.__to_environment(
                environment_model,
            )

    def update(
        self,
        environment: BuildEnvironment,
    ) -> BuildEnvironment | None:
        """
        Atualiza um ambiente existente.
        """

        if environment is None:
            raise ValueError(
                "BuildEnvironment não foi informado."
            )

        with self.__database_connection.create_session() as session:
            statement = (
                select(EnvironmentModel)
                .where(
                    EnvironmentModel.id == environment.id,
                )
            )

            environment_model = (
                session.scalars(
                    statement,
                )
                .first()
            )

            if environment_model is None:
                return None

            environment_model.name = environment.name
            environment_model.resolver = environment.resolver
            environment_model.root_path = str(
                environment.root_path,
            )

            session.commit()

            return self.__to_environment(
                environment_model,
            )

    @staticmethod
    def __to_environment(
        environment_model: EnvironmentModel,
    ) -> BuildEnvironment:
        """
        Converte o modelo SQLAlchemy para o modelo de domínio.
        """

        return BuildEnvironment(
            id=environment_model.id,
            name=environment_model.name,
            resolver=environment_model.resolver,
            root_path=Path(
                environment_model.root_path,
            ),
        )