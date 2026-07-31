"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : command_argument.py
Descrição : Representa um argumento de linha de comando.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class CommandArgument(BaseModel):
    """
    Representa um argumento de um comando.
    """

    value: str