"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_file_action.py
Descrição : Representa uma ação de sincronização de arquivo do Setup.
--------------------------------------------------------------------
"""

from enum import Enum


class SetupFileAction(
    str,
    Enum,
):
    """
    Representa uma ação necessária para sincronizar
    um arquivo do Setup.
    """

    KEEP = "keep"

    UPDATE = "update"

    ADD = "add"

    REMOVE = "remove"