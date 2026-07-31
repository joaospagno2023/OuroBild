"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_context.py
Descrição : Contexto compartilhado durante toda a execução da Pipeline.
--------------------------------------------------------------------
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PipelineContext:
    """
    Contexto compartilhado entre todas as etapas da Pipeline.

    Cada Step pode consultar e adicionar informações neste objeto.
    """

    variables: dict[str, Any] = field(default_factory=dict)

    artifacts: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)