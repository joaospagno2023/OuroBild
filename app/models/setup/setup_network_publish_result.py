"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_network_publish_result.py
Descrição : Resultado da publicação de um Setup na rede.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel


class SetupNetworkPublishResult(BaseModel):
    """Representa o resultado da publicação de um Setup na rede."""

    success: bool

    message: str

    project_id: str

    source_path: Path | None = None

    destination_path: Path | None = None

    backup_path: Path | None = None

    backup_created: bool = False

    backup_removed: bool = False

    files_copied: int = 0

    duration_seconds: float = 0.0