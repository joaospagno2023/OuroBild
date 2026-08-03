"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_execution.py
Descrição : Representa o resultado completo de uma Build.
--------------------------------------------------------------------
"""

from dataclasses import dataclass, field

from app.models.build.build_error import BuildError
from app.models.build.build_summary import BuildSummary
from app.models.build.build_warning import BuildWarning


@dataclass
class BuildExecution:
    """
    Resultado completo da Build.
    """

    summary: BuildSummary = field(
        default_factory=BuildSummary,
    )

    errors: list[BuildError] = field(
        default_factory=list,
    )

    warnings: list[BuildWarning] = field(
        default_factory=list,
    )