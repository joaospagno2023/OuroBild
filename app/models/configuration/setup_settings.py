"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_settings.py
Descrição : Representa as configurações utilizadas na geração
            do Setup.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel

from app.models.setup.setup_engine import (
    SetupEngine,
)


class SetupSettings(
    BaseModel,
):
    """
    Representa as configurações utilizadas
    durante a geração do Setup.
    """

    engine: SetupEngine

    output_root: Path