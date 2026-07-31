"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline.py
Descrição : Representa uma Pipeline de execução.
--------------------------------------------------------------------
"""

from dataclasses import dataclass, field

from app.models.pipeline.pipeline_configuration import (
    PipelineConfiguration,
)
from app.pipeline.abstractions.pipeline_step import PipelineStep


@dataclass(slots=True)
class Pipeline:
    """
    Representa uma Pipeline composta por uma sequência de Steps.
    """

    name: str = "Default"

    description: str = ""

    configuration: PipelineConfiguration = field(
        default_factory=PipelineConfiguration,
    )

    steps: list[PipelineStep] = field(
        default_factory=list,
    )