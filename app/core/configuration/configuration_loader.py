"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : configuration_loader.py
Descrição : Responsável pelo carregamento das configurações da aplicação.
--------------------------------------------------------------------
"""

# Bibliotecas padrão
import json
from pathlib import Path

# Models
from app.models.configuration.app_settings import AppSettings


class ConfigurationLoader:
    """
    Responsável por carregar os arquivos de configuração.
    """

    def __init__(self, config_path: Path):
        """
        Inicializa o carregador de configurações.

        Args:
            config_path: Caminho da pasta config.
        """

        self._config_path = config_path

    def load_settings(self) -> AppSettings:
        """
        Carrega o arquivo settings.json.

        Returns:
            AppSettings
        """

        file_path = self._config_path / "settings.json"

        with file_path.open(
            mode="r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return AppSettings.model_validate(data)