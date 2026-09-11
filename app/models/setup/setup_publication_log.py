"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publication_log.py
Descrição : Representa um evento persistido de publicação de Setup.
--------------------------------------------------------------------
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class SetupPublicationLog:
    """Representa um evento do histórico de publicação em lote."""

    batch_id: str
    timestamp: datetime
    level: str
    event_type: str
    message: str
    project_id: str | None = None
    execution_id: str | None = None
    details: str | None = None
