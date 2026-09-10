"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publication_mode.py
Descrição : Define o modo de publicação do Setup.
--------------------------------------------------------------------
"""

from enum import Enum


class SetupPublicationMode(str, Enum):
    """Define o destino de publicação do Setup."""

    LOCAL = "local"
    NETWORK = "network"