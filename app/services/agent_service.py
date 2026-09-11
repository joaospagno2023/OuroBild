"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : agent_service.py
Descrição : Regras de aplicação relacionadas aos Agents.
--------------------------------------------------------------------
"""

from app.models.agent.agent_heartbeat_request import (
    AgentHeartbeatRequest,
)
from app.models.agent.agent_registration_request import (
    AgentRegistrationRequest,
)
from app.models.agent.agent_response import AgentResponse
from app.repositories.sql_agent_repository import SqlAgentRepository


class AgentService:
    """Gerencia registro e heartbeat dos Agents."""

    def __init__(
        self,
        repository: SqlAgentRepository,
    ) -> None:
        if repository is None:
            raise ValueError(
                "SqlAgentRepository não foi informado."
            )

        self.__repository = repository

    def register(
        self,
        request: AgentRegistrationRequest,
    ) -> AgentResponse:
        result = self.__repository.register(
            name=request.name,
            machine_name=request.machine_name,
            user_name=request.user_name,
            version=request.version,
        )

        return AgentResponse.model_validate(
            self.__normalize(result),
        )

    def heartbeat(
        self,
        agent_id: int,
        request: AgentHeartbeatRequest,
    ) -> AgentResponse | None:
        result = self.__repository.heartbeat(
            agent_id=agent_id,
            version=request.version,
        )

        if result is None:
            return None

        return AgentResponse.model_validate(
            self.__normalize(result),
        )

    def get_all(self) -> list[AgentResponse]:
        return [
            AgentResponse.model_validate(
                self.__normalize(item),
            )
            for item in self.__repository.get_all()
        ]

    def __normalize(
        self,
        data: dict[str, object],
    ) -> dict[str, object]:
        """Normaliza os nomes retornados pelo SQL Server."""

        return {
            "id": int(data["Id"]),
            "name": str(data["Name"]),
            "machine_name": str(data["MachineName"]),
            "user_name": str(data["UserName"]),
            "version": str(data["Version"]),
            "status": str(data["Status"]),
            "last_heartbeat": data["LastHeartbeat"],
            "created_at": data["CreatedAt"],
            "updated_at": data["UpdatedAt"],
        }
