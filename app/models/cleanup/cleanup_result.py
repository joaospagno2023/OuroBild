"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : cleanup_result.py
Descrição : Resultado da execução da limpeza do Build.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel, Field


class CleanupResult(BaseModel):
    """
    Representa o resultado de uma execução de Cleanup.
    """

    workspace_path: Path

    dry_run: bool = False

    files_analyzed: int = 0

    files_removed: list[Path] = Field(
        default_factory=list,
    )

    files_preserved: list[Path] = Field(
        default_factory=list,
    )

    directories_analyzed: int = 0

    directories_removed: list[Path] = Field(
        default_factory=list,
    )

    directories_preserved: list[Path] = Field(
        default_factory=list,
    )

    errors: list[str] = Field(
        default_factory=list,
    )

    @property
    def success(self) -> bool:
        """
        Indica se a limpeza terminou sem erros.
        """

        return not self.errors