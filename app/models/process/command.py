"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : command.py
Descrição : Representa um comando executável.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel, Field

from app.models.process.command_argument import CommandArgument


class Command(BaseModel):
    """
    Representa um comando a ser executado.
    """

    executable: Path

    working_directory: Path

    arguments: list[CommandArgument] = Field(
        default_factory=list,
    )