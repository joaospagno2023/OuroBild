"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : authentication_service.py
Descrição : Executa a autenticação dos usuários.
--------------------------------------------------------------------
"""

from fastapi import (
    HTTPException,
    status,
)

from app.abstractions.user_repository import (
    UserRepository,
)

from app.core.security.jwt_service import (
    JwtService,
)

from app.core.security.password_service import (
    PasswordService,
)

from app.models.auth.token import (
    TokenResponse,
)


class AuthenticationService:
    """
    Responsável pela autenticação dos usuários.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        jwt_service: JwtService,
    ) -> None:
        """
        Inicializa o serviço de autenticação.
        """

        if user_repository is None:
            raise ValueError(
                "UserRepository não foi informado."
            )

        if password_service is None:
            raise ValueError(
                "PasswordService não foi informado."
            )

        if jwt_service is None:
            raise ValueError(
                "JwtService não foi informado."
            )

        self.__user_repository = (
            user_repository
        )

        self.__password_service = (
            password_service
        )

        self.__jwt_service = (
            jwt_service
        )

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> TokenResponse:
        """
        Autentica um usuário e cria o JWT.

        Args:
            username: Nome do usuário.
            password: Senha.

        Returns:
            Token JWT.

        Raises:
            HTTPException:
                Quando a autenticação falha.
        """

        credentials = (
            self.__user_repository
            .get_by_username(
                username,
            )
        )

        if credentials is None:
            raise self.__invalid_credentials()

        if not credentials.user.is_active:
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail="Usuário inativo.",
            )

        password_valid = (
            self.__password_service.verify(
                password=password,
                password_hash=(
                    credentials.password_hash
                ),
            )
        )

        if not password_valid:
            raise self.__invalid_credentials()

        access_token = (
            self.__jwt_service
            .create_access_token(
                user_id=credentials.user.id,
                username=credentials.user.username,
            )
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=(
                self.__jwt_service
                .expiration_seconds()
            ),
        )

    @staticmethod
    def __invalid_credentials() -> HTTPException:
        """
        Cria a exceção de credenciais inválidas.
        """

        return HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Usuário ou senha inválidos.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )