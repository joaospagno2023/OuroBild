"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_type.py
Descrição : Define o tipo do projeto para geração do Setup.
--------------------------------------------------------------------
"""

from enum import Enum


class ProjectType(
    str,
    Enum,
):
    """
    Define a categoria do projeto.
    """

    CLIENT = "client"

    SERVER = "server"