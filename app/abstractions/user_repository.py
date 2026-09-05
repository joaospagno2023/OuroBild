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

from app.models.auth.user import (
    User,
)

from app.models.auth.user_credentials import (
    UserCredentials,
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

        Args:
            username: Nome do usuário.

        Returns:
            Credenciais do usuário ou None.
        """

        raise NotImplementedError

    @abstractmethod
    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        """
        Localiza um usuário pelo identificador.

        Args:
            user_id: Identificador do usuário.

        Returns:
            Usuário encontrado ou None.
        """

        raise NotImplementedError