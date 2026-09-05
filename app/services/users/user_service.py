"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : user_service.py
Descrição : Executa operações relacionadas aos usuários.
--------------------------------------------------------------------
"""

from app.abstractions.user_repository import (
    UserRepository,
)

from app.core.security.password_service import (
    PasswordService,
)

from app.models.auth.create_user_request import (
    CreateUserRequest,
)

from app.models.auth.update_user_request import (
    UpdateUserRequest,
)

from app.models.auth.user import (
    User,
)


class UserService:
    """
    Responsável pelas operações de usuários.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
    ) -> None:

        if user_repository is None:
            raise ValueError(
                "UserRepository não foi informado."
            )

        if password_service is None:
            raise ValueError(
                "PasswordService não foi informado."
            )

        self.__user_repository = (
            user_repository
        )

        self.__password_service = (
            password_service
        )

    def get_all(
        self,
    ) -> list[User]:
        """
        Retorna todos os usuários.
        """

        return self.__user_repository.get_all()

    def create(
        self,
        request: CreateUserRequest,
    ) -> User:
        """
        Cria um novo usuário.
        """

        if request is None:
            raise ValueError(
                "CreateUserRequest não foi informado."
            )

        username = request.username.strip()

        display_name = (
            request.display_name.strip()
        )

        if not username:
            raise ValueError(
                "Username não foi informado."
            )

        if not display_name:
            raise ValueError(
                "DisplayName não foi informado."
            )

        if not request.password:
            raise ValueError(
                "Password não foi informado."
            )

        existing_user = (
            self.__user_repository.get_by_username(
                username,
            )
        )

        if existing_user is not None:
            raise ValueError(
                "Username já está cadastrado."
            )

        password_hash = (
            self.__password_service.hash(
                request.password,
            )
        )

        normalized_request = (
            CreateUserRequest(
                username=username,
                display_name=display_name,
                email=(
                    request.email.strip()
                    if request.email
                    else None
                ),
                password=request.password,
                is_active=request.is_active,
                must_change_password=(
                    request.must_change_password
                ),
            )
        )

        return self.__user_repository.create(
            request=normalized_request,
            password_hash=password_hash,
        )

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

        display_name = (
            request.display_name.strip()
        )

        if not display_name:
            raise ValueError(
                "DisplayName não foi informado."
            )

        normalized_request = (
            UpdateUserRequest(
                display_name=display_name,
                email=(
                    request.email.strip()
                    if request.email
                    else None
                ),
                is_active=request.is_active,
                must_change_password=(
                    request.must_change_password
                ),
            )
        )

        return self.__user_repository.update(
            user_id=user_id,
            request=normalized_request,
        )

    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> User:
        """
        Altera a senha do usuário autenticado.
        """

        if user is None:
            raise ValueError(
                "Usuário não foi informado."
            )

        if not current_password:
            raise ValueError(
                "Senha atual não foi informada."
            )

        if not new_password:
            raise ValueError(
                "Nova senha não foi informada."
            )

        if current_password == new_password:
            raise ValueError(
                "A nova senha deve ser diferente da senha atual."
            )

        credentials = (
            self.__user_repository.get_by_username(
                user.username,
            )
        )

        if credentials is None:
            raise ValueError(
                "Usuário não encontrado."
            )

        password_valid = (
            self.__password_service.verify(
                password=current_password,
                password_hash=(
                    credentials.password_hash
                ),
            )
        )

        if not password_valid:
            raise ValueError(
                "Senha atual inválida."
            )

        password_hash = (
            self.__password_service.hash(
                new_password,
            )
        )

        return self.__user_repository.update_password(
            user_id=user.id,
            password_hash=password_hash,
            must_change_password=False,
        )
