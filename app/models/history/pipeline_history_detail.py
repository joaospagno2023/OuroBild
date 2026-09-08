"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_history_detail.py
Descrição : Detalhes de uma execução do histórico.
--------------------------------------------------------------------
"""

from typing import Any

from app.models.history.pipeline_history_item import (
    PipelineHistoryItem,
)


class PipelineHistoryDetail(PipelineHistoryItem):
    """
    Representa os dados completos de uma execução persistida.
    """

    output_folder: str | None
    artifacts: list[str]
    steps: list[dict[str, Any]]
    build: dict[str, Any] | None
    publish: dict[str, Any] | None
