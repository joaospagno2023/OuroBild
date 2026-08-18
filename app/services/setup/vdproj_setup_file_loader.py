"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : vdproj_setup_file_loader.py
Descrição : Carrega os arquivos pertencentes a um projeto .vdproj.
--------------------------------------------------------------------
"""

import re
from pathlib import Path

from app.models.setup.setup_file import (
    SetupFile,
)

from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)


class VdprojSetupFileLoader:
    """
    Carrega os arquivos DLL existentes em um projeto .vdproj.

    Este serviço somente lê o projeto.
    Não altera o arquivo.
    """

    def __init__(
        self,
        parser: VdprojBlockParser,
    ) -> None:
        """
        Inicializa o Loader.
        """

        if parser is None:
            raise ValueError(
                "VdprojBlockParser não foi informado."
            )

        self.__parser = parser

    def load(
        self,
        setup_project_path: Path,
        publish_path: Path,
    ) -> list[SetupFile]:
        """
        Carrega os arquivos DLL existentes no .vdproj.

        O publish_path é utilizado para montar o caminho
        físico esperado de cada arquivo.
        """

        if setup_project_path is None:
            raise ValueError(
                "SetupProjectPath "
                "não foi informado."
            )

        if publish_path is None:
            raise ValueError(
                "PublishPath "
                "não foi informado."
            )

        setup_project_path = Path(
            setup_project_path,
        )

        publish_path = Path(
            publish_path,
        )

        if not setup_project_path.exists():
            raise FileNotFoundError(
                "Projeto Setup não encontrado: "
                f"{setup_project_path}"
            )

        if not setup_project_path.is_file():
            raise ValueError(
                "Projeto Setup não é um arquivo: "
                f"{setup_project_path}"
            )

        if not publish_path.exists():
            raise FileNotFoundError(
                "PublishPath não encontrado: "
                f"{publish_path}"
            )

        if not publish_path.is_dir():
            raise ValueError(
                "PublishPath não é um diretório: "
                f"{publish_path}"
            )

        content = (
            setup_project_path.read_text(
                encoding="utf-8",
            )
        )

        return self.__load_files(
            content=content,
            publish_path=publish_path,
        )

    def __load_files(
        self,
        content: str,
        publish_path: Path,
    ) -> list[SetupFile]:
        """
        Localiza os arquivos DLL existentes no conteúdo.
        """

        result: list[SetupFile] = []

        names = re.findall(
            r'"Name"\s*=\s*"8:([^"]+\.dll)"',
            content,
            flags=re.IGNORECASE,
        )

        processed: set[str] = set()

        for file_name in names:

            key = file_name.lower()

            if key in processed:
                continue

            processed.add(key)

            try:

                block = (
                    self.__parser.find_file_block(
                        content=content,
                        file_name=file_name,
                    )
                )

            except ValueError:
                continue

            source_path = (
                self.__extract_property(
                    content=block.content,
                    property_name="SourcePath",
                )
            )

            if source_path is None:
                continue

            assembly_display_name = (
                self.__extract_property(
                    content=block.content,
                    property_name=(
                        "AssemblyAsmDisplayName"
                    ),
                )
            )

            result.append(
                SetupFile(
                    name=file_name,
                    source_path=source_path,
                    publish_path=(
                        publish_path
                        / file_name
                    ),
                    assembly_display_name=(
                        assembly_display_name
                    ),
                )
            )

        return result

    @staticmethod
    def __extract_property(
        content: str,
        property_name: str,
    ) -> str | None:
        """
        Extrai uma propriedade string do bloco.
        """

        pattern = (
            rf'"{re.escape(property_name)}"\s*='
            rf'\s*"8:([^"]*)"'
        )

        match = re.search(
            pattern,
            content,
        )

        if match is None:
            return None

        return match.group(1)