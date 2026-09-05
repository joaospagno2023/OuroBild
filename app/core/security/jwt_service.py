"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : jwt_service.py
Descrição : Serviço responsável pela criação de tokens JWT.
--------------------------------------------------------------------
"""

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt

from app.models.configuration.security_settings import (
    SecuritySettings,
)


class JwtService:
    """
    Responsável pela criação e validação de tokens JWT.
    """

    def __init__(
        self,
        settings: SecuritySettings,
    ) -> None:
        """
        Inicializa o serviço JWT.

        Args:
            settings:
                Configurações de segurança.
        """

        if settings is None:
            raise ValueError(
                "SecuritySettings não foi informado."
            )

        if not settings.jwt_secret:
            raise ValueError(
                "JWT Secret não foi configurado."
            )

        if settings.token_expiration_minutes <= 0:
            raise ValueError(
                "A expiração do JWT deve ser maior que zero."
            )

        self.__settings = settings

    def create_access_token(
        self,
        user_id: int,
        username: str,
    ) -> str:
        """
        Cria um token de acesso.
        """

        now = datetime.now(
            timezone.utc,
        )

        expiration = (
            now
            + timedelta(
                minutes=(
                    self.__settings
                    .token_expiration_minutes
                ),
            )
        )

        payload = {
            "sub": str(user_id),
            "username": username,
            "iat": int(
                now.timestamp(),
            ),
            "exp": int(
                expiration.timestamp(),
            ),
        }

        return jwt.encode(
            payload,
            self.__settings.jwt_secret,
            algorithm=self.__settings.jwt_algorithm,
        )

    def decode(
        self,
        token: str,
    ) -> dict:
        """
        Decodifica e valida um token JWT.
        """

        if not token:
            raise ValueError(
                "Token não foi informado."
            )

        return jwt.decode(
            token,
            self.__settings.jwt_secret,
            algorithms=[
                self.__settings.jwt_algorithm,
            ],
        )

    def expiration_seconds(
        self,
    ) -> int:
        """
        Retorna o tempo de expiração do token em segundos.
        """

        return (
            self.__settings
            .token_expiration_minutes
            * 60
        )