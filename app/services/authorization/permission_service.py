"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : permission_service.py
Descrição : Serviço central de autorização do OuroBuild.
--------------------------------------------------------------------
"""

from app.abstractions.permission_repository import (
    PermissionRepository,
)


class PermissionService:
    """
    Centraliza as regras de consulta das permissões do usuário.
    """

    def __init__(
        self,
        permission_repository: PermissionRepository,
    ) -> None:
        """
        Inicializa o serviço.

        Args:
            permission_repository:
                Repositório responsável por consultar permissões.
        """
        if permission_repository is None:
            raise ValueError(
                "PermissionRepository não foi informado."
            )

        self.__permission_repository = (
            permission_repository
        )

    def has_permission(
        self,
        user_id: int,
        permission_key: str,
    ) -> bool:
        """
        Verifica se o usuário possui uma permissão.
        """
        if user_id <= 0:
            raise ValueError(
                "UserId deve ser maior que zero."
            )

        if not permission_key:
            raise ValueError(
                "PermissionKey não foi informado."
            )

        return self.__permission_repository.has_permission(
            user_id=user_id,
            permission_key=permission_key,
        )

    def get_permissions(
        self,
        user_id: int,
    ) -> list[str]:
        """
        Retorna todas as permissões ativas do usuário.
        """
        if user_id <= 0:
            raise ValueError(
                "UserId deve ser maior que zero."
            )

        return self.__permission_repository.get_permissions(
            user_id=user_id,
        )