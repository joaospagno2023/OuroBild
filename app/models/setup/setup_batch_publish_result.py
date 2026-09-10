"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_batch_publish_result.py
Descrição : Representa o resultado da publicação em lote de Setups.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel

from app.models.setup.setup_network_publish_result import (
    SetupNetworkPublishResult,
)


class SetupBatchPublishResult(
    BaseModel,
):
    """
    Resultado da publicação em lote de uma versão de Setup.
    """

    success: bool

    message: str

    execution_ids: list[str]

    project_ids: list[str]

    source_path: Path | None = None

    publication: SetupNetworkPublishResult | None = None
