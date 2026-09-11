"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : agent_router.py
Descrição : Endpoints utilizados pelo OuroBuild Agent.
--------------------------------------------------------------------
"""

from fastapi import APIRouter, HTTPException, Request, status

from app.models.agent.agent_heartbeat_request import (
    AgentHeartbeatRequest,
)
from app.models.agent.agent_registration_request import (
    AgentRegistrationRequest,
)
from app.models.agent.agent_response import AgentResponse
from app.services.agent_service import AgentService


router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


def get_agent_service(
    request: Request,
) -> AgentService:
    """Retorna a instância compartilhada do serviço de Agents."""

    service = getattr(
        request.app.state,
        "agent_service",
        None,
    )

    if service is None:
        bootstrap = request.app.state.bootstrap
        service = AgentService(
            repository=bootstrap.agent_repository,
        )
        request.app.state.agent_service = service

    return service


@router.post(
    "/register",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
)
def register_agent(
    request: Request,
    registration: AgentRegistrationRequest,
) -> AgentResponse:
    """Registra ou atualiza um Agent."""

    return get_agent_service(request).register(
        registration,
    )


@router.post(
    "/{agent_id}/heartbeat",
    response_model=AgentResponse,
)
def heartbeat_agent(
    request: Request,
    agent_id: int,
    heartbeat: AgentHeartbeatRequest,
) -> AgentResponse:
    """Atualiza o heartbeat de um Agent."""

    result = get_agent_service(request).heartbeat(
        agent_id=agent_id,
        request=heartbeat,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent não encontrado.",
        )

    return result


@router.get(
    "",
    response_model=list[AgentResponse],
)
def get_agents(
    request: Request,
) -> list[AgentResponse]:
    """Lista os Agents cadastrados."""

    return get_agent_service(request).get_all()
