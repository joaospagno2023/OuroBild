"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : advanced_installer_setup_definition_loader.py
Descrição : Carrega a definição de Setup a partir de um projeto
            Advanced Installer (.aip).
--------------------------------------------------------------------
"""

import re

from pathlib import Path

from app.models.setup.setup_definition import (
    SetupDefinition,
)


class AdvancedInstallerSetupDefinitionLoader:
    """
    Carrega as informações principais de um arquivo .aip.

    O Loader não gera o Setup.

    Sua responsabilidade é apenas ler o projeto Advanced Installer
    existente e transformá-lo em um SetupDefinition.
    """

    def load(
        self,
        aip_path: Path,
        project_id: str,
        configuration: str,
        platform: str,
        output_msi: Path,
    ) -> SetupDefinition:
        """
        Carrega a definição do Setup a partir do AIP.
        """

        if aip_path is None:
            raise ValueError(
                "O arquivo AIP não foi informado."
            )

        if not project_id or not project_id.strip():
            raise ValueError(
                "O identificador do projeto "
                "não foi informado."
            )

        if not configuration or not configuration.strip():
            raise ValueError(
                "A configuração do Setup "
                "não foi informada."
            )

        if not platform or not platform.strip():
            raise ValueError(
                "A plataforma do Setup "
                "não foi informada."
            )

        if output_msi is None:
            raise ValueError(
                "O caminho do MSI de saída "
                "não foi informado."
            )

        aip_path = Path(
            aip_path,
        )

        output_msi = Path(
            output_msi,
        )

        if not aip_path.exists():
            raise FileNotFoundError(
                "Arquivo AIP não encontrado: "
                f"{aip_path}"
            )

        if not aip_path.is_file():
            raise ValueError(
                "O caminho informado para o AIP "
                "não é um arquivo: "
                f"{aip_path}"
            )

        content = self.__read_file(
            aip_path,
        )

        product_name = self.__extract_property(
            content=content,
            property_name="ProductName",
        )

        manufacturer = self.__extract_property(
            content=content,
            property_name="Manufacturer",
        )

        version = self.__extract_property(
            content=content,
            property_name="ProductVersion",
        )

        return SetupDefinition(
            project_id=project_id.strip(),
            name=product_name,
            product_name=product_name,
            manufacturer=manufacturer,
            version=version,
            configuration=configuration.strip(),
            platform=platform.strip(),
            solution_path=aip_path.parent,
            setup_project_path=aip_path,
            output_msi=output_msi,
        )

    @staticmethod
    def __read_file(
        aip_path: Path,
    ) -> str:
        """
        Lê o arquivo AIP.

        Primeiro tenta UTF-8.

        Caso o arquivo possua caracteres incompatíveis,
        tenta Windows-1252.
        """

        try:

            return aip_path.read_text(
                encoding="utf-8",
            )

        except UnicodeDecodeError:

            return aip_path.read_text(
                encoding="cp1252",
            )

    @staticmethod
    def __extract_property(
        content: str,
        property_name: str,
    ) -> str:
        """
        Extrai uma propriedade do AIP.

        Exemplo:

            <ROW Property="ProductName"
                 Value="OuroNet"/>

        retorna:

            OuroNet
        """

        pattern = re.compile(
            r'<ROW\b'
            r'(?=[^>]*\bProperty\s*=\s*"'
            + re.escape(
                property_name,
            )
            + r'")'
            r'[^>]*\bValue\s*=\s*"'
            r'([^"]*)'
            r'"[^>]*/?>',
            re.IGNORECASE | re.DOTALL,
        )

        match = pattern.search(
            content,
        )

        if match is None:
            raise ValueError(
                f"A propriedade '{property_name}' "
                "não foi encontrada no AIP."
            )

        value = match.group(
            1,
        ).strip()

        if not value:
            raise ValueError(
                f"A propriedade '{property_name}' "
                "está vazia no AIP."
            )

        return value