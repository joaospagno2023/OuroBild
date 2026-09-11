"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publication_batch.py
Descrição : Representa uma publicação em lote de Setups.
--------------------------------------------------------------------
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class SetupPublicationBatch:
    """Representa uma operação de publicação em lote."""

    batch_id: str
    version: str
    revision: int
    source_path: Path
    destination_path: Path | None
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    elapsed_seconds: float | None = None
    total_setups: int = 0
    completed_setups: int = 0
    failed_setups: int = 0
    message: str | None = None
