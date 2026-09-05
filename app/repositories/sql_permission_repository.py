"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_permission_repository.py
Descrição : Repositório de permissões utilizando SQL Server.
--------------------------------------------------------------------
"""

from sqlalchemy import text

from app.abstractions.permission_repository import (
    PermissionRepository,
)
from app.database.connection import DatabaseConnection


class SqlPermissionRepository(PermissionRepository):
    """
    Implementação do repositório de permissões para SQL Server.
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

    def has_permission(
        self,
        user_id: int,
        permission_key: str,
    ) -> bool:
        """
        Verifica se o usuário possui uma determinada permissão ativa.
        """
        if user_id <= 0:
            raise ValueError(
                "UserId deve ser maior que zero."
            )

        if not permission_key:
            raise ValueError(
                "PermissionKey não foi informado."
            )

        statement = text(
            """
            SELECT TOP 1
                1
            FROM dbo.UserRoles AS ur
            INNER JOIN dbo.Roles AS r
                ON r.Id = ur.RoleId
            INNER JOIN dbo.RolePermissions AS rp
                ON rp.RoleId = r.Id
            INNER JOIN dbo.Permissions AS p
                ON p.Id = rp.PermissionId
            INNER JOIN dbo.Users AS u
                ON u.Id = ur.UserId
            WHERE ur.UserId = :user_id
              AND u.IsActive = 1
              AND r.IsActive = 1
              AND p.IsActive = 1
              AND p.[Key] = :permission_key
            """
        )

        with self.__database_connection.create_session() as session:
            result = session.execute(
                statement,
                {
                    "user_id": user_id,
                    "permission_key": permission_key,
                },
            ).first()

        return result is not None

    def get_permissions(
        self,
        user_id: int,
    ) -> list[str]:
        """
        Retorna as permissões ativas do usuário.
        """
        if user_id <= 0:
            raise ValueError(
                "UserId deve ser maior que zero."
            )

        statement = text(
            """
            SELECT DISTINCT
                p.[Key]
            FROM dbo.UserRoles AS ur
            INNER JOIN dbo.Roles AS r
                ON r.Id = ur.RoleId
            INNER JOIN dbo.RolePermissions AS rp
                ON rp.RoleId = r.Id
            INNER JOIN dbo.Permissions AS p
                ON p.Id = rp.PermissionId
            INNER JOIN dbo.Users AS u
                ON u.Id = ur.UserId
            WHERE ur.UserId = :user_id
              AND u.IsActive = 1
              AND r.IsActive = 1
              AND p.IsActive = 1
            ORDER BY
                p.[Key]
            """
        )

        with self.__database_connection.create_session() as session:
            rows = session.execute(
                statement,
                {
                    "user_id": user_id,
                },
            ).all()

        return [
            row[0]
            for row in rows
        ]