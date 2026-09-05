"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : permission_repository.py
Descrição : Contrato para consulta das permissões do usuário.
--------------------------------------------------------------------
"""

from abc import ABC, abstractmethod


class PermissionRepository(ABC):
    """
    Define o contrato para consulta das permissões de um usuário.
    """

    @abstractmethod
    def has_permission(
        self,
        user_id: int,
        permission_key: str,
    ) -> bool:
        """
        Verifica se o usuário possui uma determinada permissão.
        """
        raise NotImplementedError

    @abstractmethod
    def get_permissions(
        self,
        user_id: int,
    ) -> list[str]:
        """
        Retorna as permissões ativas do usuário.
        """
        raise NotImplementedError