"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_output_cleanup_result.py
Descrição : Resultado da preparação da pasta de saída dos Setups.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class SetupOutputCleanupResult(BaseModel):
    """
    Representa o resultado da preparação da pasta de saída dos Setups.
    """

    success: bool
    message: str
    output_root: str
    preserved_path: str
    removed_items: int = 0
