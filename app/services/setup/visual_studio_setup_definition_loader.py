"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : visual_studio_setup_definition_loader.py
Descrição : Carrega a definição de Setup a partir de um projeto
            Visual Studio Installer (.vdproj).
--------------------------------------------------------------------
"""

import re
from pathlib import Path

from app.models.setup.setup_definition import (
    SetupDefinition,
)


class VisualStudioSetupDefinitionLoader:
    """
    Carrega as informações principais de um arquivo .vdproj.

    O Loader não gera o Setup.

    Sua responsabilidade é apenas ler o projeto existente
    e transformá-lo em um SetupDefinition.
    """

    def load(
        self,
        setup_project_path: Path,
        solution_path: Path,
        configuration: str,
        platform: str = "AnyCPU",
    ) -> SetupDefinition:
        """
        Carrega a definição do Setup.

        Args:
            setup_project_path:
                Caminho do arquivo .vdproj.

            solution_path:
                Caminho da solução que contém o projeto
                de Setup.

            configuration:
                Configuração utilizada para geração do Setup.

            platform:
                Plataforma utilizada pela configuração.

        Returns:
            SetupDefinition contendo as informações
            encontradas no .vdproj.

        Raises:
            ValueError:
                Quando alguma informação obrigatória não
                puder ser encontrada.

            FileNotFoundError:
                Quando algum arquivo não existir.
        """

        if setup_project_path is None:
            raise ValueError(
                "O caminho do projeto de Setup "
                "não foi informado."
            )

        if solution_path is None:
            raise ValueError(
                "O caminho da solução "
                "não foi informado."
            )

        if not configuration or not configuration.strip():
            raise ValueError(
                "A configuração do Setup "
                "não foi informada."
            )

        setup_project_path = Path(
            setup_project_path,
        )

        solution_path = Path(
            solution_path,
        )

        if not setup_project_path.exists():
            raise FileNotFoundError(
                "O projeto de Setup não foi encontrado: "
                f"{setup_project_path}"
            )

        if not setup_project_path.is_file():
            raise ValueError(
                "O caminho informado para o projeto de Setup "
                "não é um arquivo: "
                f"{setup_project_path}"
            )

        if not solution_path.exists():
            raise FileNotFoundError(
                "A solução do Setup não foi encontrada: "
                f"{solution_path}"
            )

        if not solution_path.is_file():
            raise ValueError(
                "O caminho informado para a solução "
                "não é um arquivo: "
                f"{solution_path}"
            )

        content = self.__read_file(
            setup_project_path,
        )

        project_name = self.__extract_value(
            content=content,
            field_name="ProjectName",
        )

        product_name = self.__extract_value(
            content=content,
            field_name="ProductName",
        )

        manufacturer = self.__extract_value(
            content=content,
            field_name="Manufacturer",
        )

        version = self.__extract_value(
            content=content,
            field_name="ProductVersion",
        )

        output_msi = self.__resolve_output_msi(
            content=content,
            configuration=configuration.strip(),
            setup_project_path=setup_project_path,
        )

        return SetupDefinition(
            project_id=setup_project_path.stem,
            name=project_name,
            product_name=product_name,
            manufacturer=manufacturer,
            version=version,
            configuration=configuration.strip(),
            platform=platform.strip(),
            solution_path=solution_path,
            setup_project_path=setup_project_path,
            output_msi=output_msi,
        )

    def __read_file(
        self,
        setup_project_path: Path,
    ) -> str:
        """
        Lê o arquivo .vdproj.

        Arquivos .vdproj antigos normalmente utilizam
        Windows-1252. Utilizamos essa codificação para
        preservar caracteres existentes no projeto.
        """

        try:

            return setup_project_path.read_text(
                encoding="cp1252",
            )

        except UnicodeDecodeError:

            return setup_project_path.read_text(
                encoding="utf-8",
            )

    def __extract_value(
        self,
        content: str,
        field_name: str,
    ) -> str:
        """
        Extrai o valor de uma propriedade simples do .vdproj.

        Exemplo:

            "ProductName" = "8:OuroNetApp"

        retorna:

            OuroNetApp
        """

        pattern = (
            rf'"{re.escape(field_name)}"\s*=\s*"8:(.*?)"'
        )

        match = re.search(
            pattern,
            content,
            flags=re.DOTALL,
        )

        if match is None:
            raise ValueError(
                f"O campo '{field_name}' não foi encontrado "
                "no projeto de Setup."
            )

        value = match.group(
            1,
        ).strip()

        if not value:
            raise ValueError(
                f"O campo '{field_name}' está vazio "
                "no projeto de Setup."
            )

        return value

    def __resolve_output_msi(
        self,
        content: str,
        configuration: str,
        setup_project_path: Path,
    ) -> Path:
        """
        Resolve o nome do MSI configurado no .vdproj.
        """

        configuration_pattern = (
            rf'"{re.escape(configuration)}"\s*'
            r'\{(.*?)\}'
        )

        configuration_match = re.search(
            configuration_pattern,
            content,
            flags=re.DOTALL,
        )

        if configuration_match is None:
            raise ValueError(
                f"A configuração '{configuration}' não foi "
                "encontrada no projeto de Setup."
            )

        configuration_content = (
            configuration_match.group(
                1,
            )
        )

        output_match = re.search(
            r'"OutputFilename"\s*=\s*"8:(.*?)"',
            configuration_content,
            flags=re.DOTALL,
        )

        if output_match is None:
            raise ValueError(
                "O campo 'OutputFilename' não foi encontrado "
                f"na configuração '{configuration}'."
            )

        output_value = (
            output_match.group(
                1,
            ).strip()
        )

        if not output_value:
            raise ValueError(
                "O campo 'OutputFilename' está vazio "
                f"na configuração '{configuration}'."
            )

        output_path = Path(
            output_value,
        )

        if output_path.is_absolute():
            return output_path

        return (
            setup_project_path.parent
            / output_path
        )