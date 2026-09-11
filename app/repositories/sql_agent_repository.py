"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_agent_repository.py
Descrição : Repositório de Agents utilizando SQL Server.
--------------------------------------------------------------------
"""

from datetime import datetime, timezone

from sqlalchemy import text

from app.database.connection import DatabaseConnection
from app.models.agent.agent_status import AgentStatus


class SqlAgentRepository:
    """Implementa a persistência dos Agents no SQL Server."""

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        if database_connection is None:
            raise ValueError(
                "DatabaseConnection não foi informado."
            )

        self.__database_connection = database_connection

    def register(
        self,
        name: str,
        machine_name: str,
        user_name: str,
        version: str,
    ) -> dict[str, object]:
        """Registra o Agent ou atualiza um registro existente."""

        now = datetime.now(timezone.utc)

        with self.__database_connection.create_session() as session:
            statement = text(
                """
                SELECT
                    Id,
                    Name,
                    MachineName,
                    UserName,
                    Version,
                    Status,
                    LastHeartbeat,
                    CreatedAt,
                    UpdatedAt
                FROM dbo.Agents
                WHERE MachineName = :machine_name
                  AND UserName = :user_name
                """
            )

            row = session.execute(
                statement,
                {
                    "machine_name": machine_name,
                    "user_name": user_name,
                },
            ).mappings().first()

            if row is None:
                insert_statement = text(
                    """
                    INSERT INTO dbo.Agents
                    (
                        Name,
                        MachineName,
                        UserName,
                        Version,
                        Status,
                        LastHeartbeat,
                        CreatedAt,
                        UpdatedAt
                    )
                    OUTPUT INSERTED.Id
                    VALUES
                    (
                        :name,
                        :machine_name,
                        :user_name,
                        :version,
                        :status,
                        :last_heartbeat,
                        :created_at,
                        :updated_at
                    )
                    """
                )

                agent_id = session.execute(
                    insert_statement,
                    {
                        "name": name,
                        "machine_name": machine_name,
                        "user_name": user_name,
                        "version": version,
                        "status": AgentStatus.ONLINE.value,
                        "last_heartbeat": now,
                        "created_at": now,
                        "updated_at": now,
                    },
                ).scalar_one()
            else:
                agent_id = int(row["Id"])

                update_statement = text(
                    """
                    UPDATE dbo.Agents
                    SET
                        Name = :name,
                        Version = :version,
                        Status = :status,
                        LastHeartbeat = :last_heartbeat,
                        UpdatedAt = :updated_at
                    WHERE Id = :id
                    """
                )

                session.execute(
                    update_statement,
                    {
                        "id": agent_id,
                        "name": name,
                        "version": version,
                        "status": AgentStatus.ONLINE.value,
                        "last_heartbeat": now,
                        "updated_at": now,
                    },
                )

            session.commit()

        return self.get_by_id(agent_id)

    def heartbeat(
        self,
        agent_id: int,
        version: str,
    ) -> dict[str, object] | None:
        """Atualiza o heartbeat de um Agent."""

        now = datetime.now(timezone.utc)

        with self.__database_connection.create_session() as session:
            statement = text(
                """
                UPDATE dbo.Agents
                SET
                    Version = :version,
                    Status = :status,
                    LastHeartbeat = :last_heartbeat,
                    UpdatedAt = :updated_at
                WHERE Id = :id
                """
            )

            result = session.execute(
                statement,
                {
                    "id": agent_id,
                    "version": version,
                    "status": AgentStatus.ONLINE.value,
                    "last_heartbeat": now,
                    "updated_at": now,
                },
            )

            if result.rowcount == 0:
                session.rollback()
                return None

            session.commit()

        return self.get_by_id(agent_id)

    def get_by_id(
        self,
        agent_id: int,
    ) -> dict[str, object] | None:
        """Retorna um Agent pelo identificador."""

        with self.__database_connection.create_session() as session:
            statement = text(
                """
                SELECT
                    Id,
                    Name,
                    MachineName,
                    UserName,
                    Version,
                    Status,
                    LastHeartbeat,
                    CreatedAt,
                    UpdatedAt
                FROM dbo.Agents
                WHERE Id = :id
                """
            )

            row = session.execute(
                statement,
                {"id": agent_id},
            ).mappings().first()

            if row is None:
                return None

            return dict(row)

    def get_all(self) -> list[dict[str, object]]:
        """Retorna todos os Agents cadastrados."""

        with self.__database_connection.create_session() as session:
            statement = text(
                """
                SELECT
                    Id,
                    Name,
                    MachineName,
                    UserName,
                    Version,
                    Status,
                    LastHeartbeat,
                    CreatedAt,
                    UpdatedAt
                FROM dbo.Agents
                ORDER BY Name
                """
            )

            rows = session.execute(statement).mappings().all()

            return [dict(row) for row in rows]
