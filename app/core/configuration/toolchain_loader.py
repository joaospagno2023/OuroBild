"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : toolchain_loader.py
Descrição : Responsável por carregar o arquivo toolchain.json.
--------------------------------------------------------------------
"""

import json

from pathlib import Path

from app.models.toolchain.toolchain_settings import (
    ToolchainSettings,
)


class ToolchainLoader:
    """
    Responsável por carregar as configurações das
    ferramentas utilizadas pelo OuroBuild.
    """

    def __init__(
        self,
        configuration_path: Path,
    ) -> None:

        self.__configuration_path = (
            configuration_path
        )

    def load(
        self,
    ) -> ToolchainSettings:
        """
        Carrega o arquivo toolchain.json.
        """

        file_path = (
            self.__configuration_path
            / "toolchain.json"
        )

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file,
            )

        return ToolchainSettings.model_validate(
            data,
        )