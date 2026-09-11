"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : agent_status.py
Descrição : Estados possíveis do Agent Runner.
--------------------------------------------------------------------
"""

from enum import Enum


class AgentStatus(str, Enum):
    """Representa o estado operacional de um Agent."""

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
