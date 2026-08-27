"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : advanced_installer_aip_file_parser.py
Descrição : Extrai referências individuais de arquivos de um
            projeto Advanced Installer (.aip).
--------------------------------------------------------------------
"""

import re

from pathlib import Path

from app.models.setup.setup_file import (
    SetupFile,
)


class AdvancedInstallerAipFileParser:
    """
    Extrai arquivos individuais de um projeto Advanced Installer.

    O parser não modifica o AIP.

    São considerados arquivos individuais os ROWs pertencentes
    ao componente:

        caphyon.advinst.msicomp.MsiFilesComponent

    Componentes de pasta sincronizada ou outros componentes
    não são considerados arquivos individuais.
    """

    __COMPONENT_PATTERN = re.compile(
        r"<COMPONENT\b"
        r"(?P<header>.*?)"
        r">"
        r"(?P<body>.*?)"
        r"</COMPONENT>",
        re.IGNORECASE | re.DOTALL,
    )

    __ROW_PATTERN = re.compile(
        r"<ROW\b"
        r"(?P<attributes>.*?)"
        r"/>",
        re.IGNORECASE | re.DOTALL,
    )

    __ATTRIBUTE_PATTERN = re.compile(
        r'(?P<name>[A-Za-z_][A-Za-z0-9_]*)'
        r"\s*=\s*"
        r'"(?P<value>(?:[^"\\]|\\.)*)"',
        re.IGNORECASE,
    )

    __MSI_FILES_COMPONENT = (
        "caphyon.advinst.msicomp.MsiFilesComponent"
    )

    __SYNCHRONIZED_FOLDER_COMPONENT = (
        "caphyon.advinst.msicomp.SynchronizedFolderComponent"
    )

    def parse(
        self,
        content: str,
        publish_path: Path,
    ) -> list[SetupFile]:
        """
        Analisa o conteúdo do AIP e retorna os arquivos
        individuais encontrados.

        :param content:
            Conteúdo completo do arquivo .aip.

        :param publish_path:
            Diretório de publicação da versão atual.

        :return:
            Lista de SetupFile.
        """

        if content is None:

            raise ValueError(
                "Conteúdo do AIP não foi informado."
            )

        if publish_path is None:

            raise ValueError(
                "PublishPath não foi informado."
            )

        publish_path = Path(
            publish_path,
        )

        results: list[SetupFile] = []

        for component_match in (
            self.__COMPONENT_PATTERN.finditer(
                content,
            )
        ):
            header = (
                component_match.group(
                    "header",
                )
            )

            body = (
                component_match.group(
                    "body",
                )
            )

            component_id = (
                self.__get_component_id(
                    header,
                )
            )

            #
            # Somente MsiFilesComponent contém arquivos
            # individuais que queremos analisar.
            #

            if not self.__is_msi_files_component(
                component_id,
            ):
                continue

            for row_match in (
                self.__ROW_PATTERN.finditer(
                    body,
                )
            ):
                attributes = (
                    self.__parse_attributes(
                        row_match.group(
                            "attributes",
                        ),
                    )
                )

                file_name = (
                    attributes.get(
                        "File",
                    )
                )

                source_path = (
                    attributes.get(
                        "SourcePath",
                    )
                )

                component = (
                    attributes.get(
                        "Component_",
                    )
                )

                #
                # Um arquivo individual precisa possuir
                # identificação, componente e origem.
                #

                if not file_name:

                    continue

                if not source_path:

                    continue

                if not component:

                    continue

                physical_name = (
                    self.__get_file_name(
                        source_path=source_path,
                        fallback=file_name,
                    )
                )

                if not physical_name:

                    continue

                #
                # Evitar duplicidade.
                #

                if self.__contains_file(
                    results=results,
                    source_path=source_path,
                ):

                    continue

                results.append(
                    SetupFile(
                        name=physical_name,
                        source_path=source_path,
                        publish_path=(
                            publish_path
                            / physical_name
                        ),
                    )
                )

        return results

    @classmethod
    def __get_component_id(
        cls,
        header: str,
    ) -> str | None:
        """
        Obtém o identificador cid do componente.
        """

        attributes = (
            cls.__parse_attributes(
                header,
            )
        )

        return (
            attributes.get(
                "cid",
            )
        )

    @classmethod
    def __is_msi_files_component(
        cls,
        component_id: str | None,
    ) -> bool:
        """
        Verifica se o componente representa arquivos
        individuais.
        """

        if not component_id:

            return False

        return (
            component_id.strip().lower()
            == cls.__MSI_FILES_COMPONENT.lower()
        )

    @classmethod
    def __is_synchronized_folder_component(
        cls,
        component_id: str | None,
    ) -> bool:
        """
        Verifica se o componente representa uma pasta
        sincronizada.
        """

        if not component_id:

            return False

        return (
            component_id.strip().lower()
            == cls.__SYNCHRONIZED_FOLDER_COMPONENT.lower()
        )

    @classmethod
    def __parse_attributes(
        cls,
        attributes_text: str,
    ) -> dict[str, str]:
        """
        Extrai os atributos de uma estrutura do AIP.

        A ordem dos atributos não é relevante.
        """

        attributes: dict[str, str] = {}

        for match in (
            cls.__ATTRIBUTE_PATTERN.finditer(
                attributes_text,
            )
        ):
            name = (
                match.group(
                    "name",
                )
            )

            value = (
                match.group(
                    "value",
                )
            )

            attributes[name] = value

        return attributes

    @staticmethod
    def __get_file_name(
        source_path: str,
        fallback: str,
    ) -> str:
        """
        Obtém o nome físico do arquivo.

        SourcePath pode conter:

            arquivo.dll

        ou:

            x64\\arquivo.dll

        ou:

            C:\\Build\\x64\\arquivo.dll
        """

        normalized_path = (
            source_path.replace(
                "\\",
                "/",
            )
        )

        file_name = (
            Path(
                normalized_path,
            ).name
        )

        if file_name:

            return file_name

        return fallback

    @classmethod
    def __contains_file(
        cls,
        results: list[SetupFile],
        source_path: str,
    ) -> bool:
        """
        Verifica se o SourcePath já foi processado.
        """

        normalized_source_path = (
            source_path
            .replace(
                "\\",
                "/",
            )
            .strip()
            .lower()
        )

        for result in results:

            existing_source_path = (
                result.source_path
                .replace(
                    "\\",
                    "/",
                )
                .strip()
                .lower()
            )

            if (
                existing_source_path
                == normalized_source_path
            ):

                return True

        return False