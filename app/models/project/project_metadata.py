"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_metadata.py
Descrição : Representa a metadata conhecida de um projeto.
--------------------------------------------------------------------
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProjectMetadata:
    """
    Representa a metadata conhecida de um projeto.
    """

    #
    # Identificação
    #

    project_id: str

    #
    # Controle
    #

    project_hash: str

    restore_hash: str | None = None

    project_last_write: datetime | None = None

    last_analysis: datetime | None = None

    analysis_version: str = "1.0"

    #
    # Arquivo da análise
    #

    analysis_file: str = "analysis.json"