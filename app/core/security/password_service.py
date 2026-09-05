"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : password_service.py
Descrição : Serviço responsável por hash e validação de senhas.
--------------------------------------------------------------------
"""

from pwdlib import PasswordHash


class PasswordService:
    """
    Responsável por proteger e validar senhas.
    """

    def __init__(
        self,
    ) -> None:
        self.__password_hash = (
            PasswordHash.recommended()
        )

    def hash(
        self,
        password: str,
    ) -> str:
        """
        Gera o hash seguro da senha.

        Args:
            password: Senha em texto puro.

        Returns:
            Hash da senha.
        """

        self.__validate_password(
            password,
        )

        return self.__password_hash.hash(
            password,
        )

    def verify(
        self,
        password: str,
        password_hash: str,
    ) -> bool:
        """
        Valida uma senha contra um hash.

        Args:
            password: Senha informada.
            password_hash: Hash armazenado.

        Returns:
            True quando a senha é válida.
        """

        self.__validate_password(
            password,
        )

        if not password_hash:
            return False

        return self.__password_hash.verify(
            password,
            password_hash,
        )

    @staticmethod
    def __validate_password(
        password: str,
    ) -> None:
        """
        Valida a senha recebida.
        """

        if not password:
            raise ValueError(
                "Password não foi informado."
            )