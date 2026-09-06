"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : logging_settings.py
Descrição : Representa as configurações do sistema de logging.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel


class LoggingSettings(
    BaseModel,
):
    """
    Representa as configurações utilizadas pelo logger.
    """

    enabled: bool = True

    path: Path = Path(
        r"C:\Custom\ourobuild\app\logs"
    )

    level: str = "INFO"