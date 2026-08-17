"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_file_sync.py
Descrição : Representa o resultado da sincronização de arquivos.
--------------------------------------------------------------------
"""

from app.models.setup.setup_file import (
    SetupFile,
)

from app.models.setup.setup_file_action import (
    SetupFileAction,
)


class SetupFileSync(
    SetupFile,
):
    """
    Representa um arquivo e a ação que deverá ser executada.
    """

    action: SetupFileAction