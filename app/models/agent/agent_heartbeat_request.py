"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : agent_heartbeat_request.py
Descrição : Dados enviados pelo Agent durante o heartbeat.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class AgentHeartbeatRequest(BaseModel):
    """Representa o heartbeat enviado por um Agent."""

    version: str
