"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : user_repository.py
Descrição : Define o contrato do repositório de usuários.
--------------------------------------------------------------------
"""

from abc import (
    ABC,
    abstractmethod,
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

from app.models.auth.user_credentials import (
    UserCredentials,
)

from app.models.auth.update_user_status_request import (
    UpdateUserStatusRequest,
)

class UserRepository(
    ABC,
):
    """
    Define as operações necessárias para usuários.
    """

    @abstractmethod
    def get_by_username(
        self,
        username: str,
    ) -> UserCredentials | None:
        """
        Localiza um usuário pelas credenciais.
        """

        raise NotImplementedError

    @abstractmethod
    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        """
        Localiza um usuário pelo identificador.
        """

        raise NotImplementedError

    @abstractmethod
    def get_all(
        self,
    ) -> list[User]:
        """
        Retorna todos os usuários.
        """

        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        request: CreateUserRequest,
        password_hash: str,
    ) -> User:
        """
        Cria um usuário.
        """

        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        user_id: int,
        request: UpdateUserRequest,
    ) -> User:
        """
        Atualiza os dados de um usuário.
        """

        raise NotImplementedError
    
    @abstractmethod
    def update_profile(
        self,
        user_id: int,
        display_name: str,
        email: str | None,
    ) -> User:
        """
        Atualiza o nome e o e-mail do próprio perfil.
        """

        raise NotImplementedError

    @abstractmethod
    def update_status(
        self,
        user_id: int,
        request: UpdateUserStatusRequest,
    ) -> User:
        """
        Atualiza somente o status de um usuário.
        """

        raise NotImplementedError
    @abstractmethod
    def update_password(
        self,
        user_id: int,
        password_hash: str,
        must_change_password: bool,
    ) -> User:
        """
        Atualiza a senha de um usuário.
        """

        raise NotImplementedError
