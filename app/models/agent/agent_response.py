"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : agent_response.py
Descrição : Resposta da API para operações do Agent.
--------------------------------------------------------------------
"""

from datetime import datetime

from pydantic import BaseModel

from app.models.agent.agent_status import AgentStatus


class AgentResponse(BaseModel):
    """Representa um Agent persistido no OuroBuild."""

    id: int
    name: str
    machine_name: str
    user_name: str
    version: str
    status: AgentStatus
    last_heartbeat: datetime | None
    created_at: datetime
    updated_at: datetime
