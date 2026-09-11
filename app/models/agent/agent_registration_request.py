"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : agent_registration_request.py
Descrição : Dados enviados pelo Agent durante o registro.
--------------------------------------------------------------------
"""

from pydantic import BaseModel, Field


class AgentRegistrationRequest(BaseModel):
    """Representa os dados de registro de um Agent."""

    name: str = Field(min_length=1, max_length=100)
    machine_name: str = Field(min_length=1, max_length=255)
    user_name: str = Field(min_length=1, max_length=255)
    version: str = Field(min_length=1, max_length=50)
