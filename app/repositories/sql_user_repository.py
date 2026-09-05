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

from app.models.auth.create_user_request import (
    CreateUserRequest,
)

from app.models.auth.update_user_request import (
    UpdateUserRequest,
)

from app.models.auth.update_user_status_request import (
    UpdateUserStatusRequest,
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

    def get_all(
        self,
    ) -> list[User]:
        """
        Retorna todos os usuários ordenados pelo username.
        """

        with self.__database_connection.create_session() as session:

            statement = (
                select(UserModel)
                .order_by(
                    UserModel.username,
                )
            )

            user_models = (
                session.scalars(
                    statement,
                )
                .all()
            )

            return [
                self.__to_user(
                    user_model,
                )
                for user_model in user_models
            ]

    def create(
        self,
        request: CreateUserRequest,
        password_hash: str,
    ) -> User:
        """
        Cria um usuário.
        """

        if request is None:
            raise ValueError(
                "CreateUserRequest não foi informado."
            )

        if not password_hash:
            raise ValueError(
                "PasswordHash não foi informado."
            )

        with self.__database_connection.create_session() as session:

            user_model = UserModel(
                username=request.username,
                password_hash=password_hash,
                display_name=request.display_name,
                email=request.email,
                is_active=request.is_active,
                must_change_password=(
                    request.must_change_password
                ),
            )

            session.add(
                user_model,
            )

            session.flush()

            user = self.__to_user(
                user_model,
            )

            session.commit()

            return user

    def update(
        self,
        user_id: int,
        request: UpdateUserRequest,
    ) -> User:
        """
        Atualiza os dados de um usuário.
        """

        if user_id <= 0:
            raise ValueError(
                "UserId deve ser maior que zero."
            )

        if request is None:
            raise ValueError(
                "UpdateUserRequest não foi informado."
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
                raise ValueError(
                    "Usuário não encontrado."
                )

            user_model.display_name = (
                request.display_name
            )

            user_model.email = request.email

            user_model.is_active = (
                request.is_active
            )

            user_model.must_change_password = (
                request.must_change_password
            )

            session.flush()

            user = self.__to_user(
                user_model,
            )

            session.commit()

            return user

    def update_status(
        self,
        user_id: int,
        request: UpdateUserStatusRequest,
    ) -> User:
        """
        Atualiza somente o status de um usuário.
        """

        if user_id <= 0:
            raise ValueError(
                "UserId deve ser maior que zero."
            )

        if request is None:
            raise ValueError(
                "UpdateUserStatusRequest não foi informado."
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
                raise ValueError(
                    "Usuário não encontrado."
                )

            user_model.is_active = (
                request.is_active
            )

            session.flush()

            user = self.__to_user(
                user_model,
            )

            session.commit()

            return user

    def update_password(
        self,
        user_id: int,
        password_hash: str,
        must_change_password: bool,
    ) -> User:
        """
        Atualiza a senha de um usuário.
        """

        if user_id <= 0:
            raise ValueError(
                "UserId deve ser maior que zero."
            )

        if not password_hash:
            raise ValueError(
                "PasswordHash não foi informado."
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
                raise ValueError(
                    "Usuário não encontrado."
                )

            user_model.password_hash = (
                password_hash
            )

            user_model.must_change_password = (
                must_change_password
            )

            session.flush()

            user = self.__to_user(
                user_model,
            )

            session.commit()

            return user

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
            must_change_password=(
                user_model.must_change_password
            ),
            created_at=user_model.created_at,
            last_login_at=user_model.last_login_at,
        )