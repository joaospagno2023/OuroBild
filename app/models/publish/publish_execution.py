"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_execution.py
Descrição : Resultado completo do Publish.
--------------------------------------------------------------------
"""

from dataclasses import dataclass, field

from app.models.publish.publish_error import PublishError
from app.models.publish.publish_summary import PublishSummary
from app.models.publish.publish_warning import PublishWarning


@dataclass(slots=True)
class PublishExecution:
    """
    Resultado completo do Publish.
    """

    summary: PublishSummary = field(
        default_factory=PublishSummary,
    )

    errors: list[PublishError] = field(
        default_factory=list,
    )

    warnings: list[PublishWarning] = field(
        default_factory=list,
    )