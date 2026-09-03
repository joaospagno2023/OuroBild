"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_execution_request.py
Descrição : Dados opcionais para execução da Pipeline com Setup.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class PipelineExecutionRequest(BaseModel):
    """Dados necessários para gerar o Setup ao final da Pipeline."""

    environment_id: str
    version: str | None = None
    revision: int | None = None
