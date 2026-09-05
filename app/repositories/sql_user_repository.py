"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_user_repository.py
Descrição : Repositório de usuários utilizando SQL Server.
--------------------------------------------------------------------
"""

from sqlalchemy import (
    select,
)

from app.abstractions.user_repository import (
    UserRepository,
)

from app.database.connection import (
    DatabaseConnection,
)

from app.database.models.user_model import (
    UserModel,
)

from app.models.auth.user import (
    User,
)

from app.models.auth.user_credentials import (
    UserCredentials,
)


class SqlUserRepository(
    UserRepository,
):
    """
    Implementação do repositório de usuários para SQL Server.
    """

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        """
        Inicializa o repositório.

        Args:
            database_connection:
                Conexão com o banco de dados.
        """

        if database_connection is None:
            raise ValueError(
                "DatabaseConnection não foi informado."
            )

        self.__database_connection = (
            database_connection
        )

    def get_by_username(
        self,
        username: str,
    ) -> UserCredentials | None:
        """
        Localiza um usuário pelo username.
        """

        if not username:
            raise ValueError(
                "Username não foi informado."
            )

        with self.__database_connection.create_session() as session:

            statement = (
                select(UserModel)
                .where(
                    UserModel.username == username,
                )
            )

            user_model = (
                session.scalars(
                    statement,
                )
                .first()
            )

            if user_model is None:
                return None

            user = self.__to_user(
                user_model,
            )

            return UserCredentials(
                user=user,
                password_hash=(
                    user_model.password_hash
                ),
                created_at=(
                    user_model.created_at
                ),
            )

    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        """
        Localiza um usuário pelo identificador.
        """

        if user_id <= 0:
            raise ValueError(
                "UserId deve ser maior que zero."
            )

        with self.__database_connection.create_session() as session:

            statement = (
                select(UserModel)
                .where(
                    UserModel.id == user_id,
                )
            )

            user_model = (
                session.scalars(
                    statement,
                )
                .first()
            )

            if user_model is None:
                return None

            return self.__to_user(
                user_model,
            )

    @staticmethod
    def __to_user(
        user_model: UserModel,
    ) -> User:
        """
        Converte o modelo SQLAlchemy para o modelo de domínio.
        """

        return User(
            id=user_model.id,
            username=user_model.username,
            display_name=user_model.display_name,
            email=user_model.email,
            is_active=user_model.is_active,
            created_at=user_model.created_at,
            last_login_at=user_model.last_login_at,
        )