"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_source_state.py
Descrição : Estado persistido dos fontes utilizado para decidir
             quando o Get Last deve ser executado.
--------------------------------------------------------------------
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProjectSourceState:
    """Representa o estado persistido dos fontes de um projeto."""

    project_id: str
    source_hash: str
    last_checked_at: datetime | None = None
    last_get_last_at: datetime | None = None
    last_build_at: datetime | None = None
