"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : advanced_installer_aip_modifier.py
Descrição : Prepara um projeto Advanced Installer (.aip) para
            geração de uma nova versão do Setup.
--------------------------------------------------------------------
"""

import re

from pathlib import Path

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.models.setup.setup_file_sync import (
    SetupFileSync,
)

from app.services.setup.setup_file_modifier import (
    SetupFileModifier,
)


class AdvancedInstallerAipModifier(
    SetupFileModifier,
):
    """
    Prepara um arquivo AIP para uma nova execução de build.

    Responsabilidades:

        - atualizar a versão do produto;
        - atualizar a origem da pasta sincronizada;
        - remover arquivos individuais obsoletos;
        - adicionar arquivos individuais novos;
        - preservar a estrutura restante do projeto;
        - trabalhar somente sobre o AIP recebido.

    Esta classe não executa o AdvancedInstaller.com.
    """

    __SYNCHRONIZED_FOLDER_COMPONENT = (
        "caphyon.advinst.msicomp."
        "SynchronizedFolderComponent"
    )

    __MSI_FILES_COMPONENT = (
        "caphyon.advinst.msicomp."
        "MsiFilesComponent"
    )

    def apply(
        self,
        aip_path: Path,
        version: str,
        publish_path: Path,
        changes: list[SetupFileSync] | None = None,
    ) -> None:
        """
        Prepara o AIP.

        :param aip_path:
            Caminho do arquivo .aip.

        :param version:
            Nova versão do produto.

        :param publish_path:
            Diretório Release que será utilizado pela
            pasta sincronizada.

        :param changes:
            Alterações de arquivos que deverão ser aplicadas
            ao AIP.
        """

        if aip_path is None:

            raise ValueError(
                "O arquivo AIP não foi informado."
            )

        aip_path = Path(
            aip_path,
        )

        if not aip_path.exists():

            raise FileNotFoundError(
                "Arquivo AIP não encontrado:\n"
                f"{aip_path}"
            )

        if not aip_path.is_file():

            raise ValueError(
                "O caminho informado para o AIP "
                "não é um arquivo:\n"
                f"{aip_path}"
            )

        if publish_path is None:

            raise ValueError(
                "A pasta de publicação não foi informada."
            )

        publish_path = Path(
            publish_path,
        )

        if not publish_path.exists():

            raise FileNotFoundError(
                "Pasta de publicação não encontrada:\n"
                f"{publish_path}"
            )

        if not publish_path.is_dir():

            raise ValueError(
                "A pasta de publicação não é um diretório:\n"
                f"{publish_path}"
            )

        if version is None:

            raise ValueError(
                "A versão do AIP não foi informada."
            )

        if not str(version).strip():

            raise ValueError(
                "A versão do AIP não foi informada."
            )

        content = (
            aip_path.read_text(
                encoding="utf-8",
            )
        )

        #
        # ============================================================
        # Atualizar versão.
        # ============================================================
        #

        content = (
            self.__replace_version(
                content=content,
                version=str(
                    version,
                ).strip(),
            )
        )

        #
        # ============================================================
        # Atualizar pasta sincronizada.
        # ============================================================
        #

        content = (
            self.__replace_synchronized_folder(
                content=content,
                publish_path=publish_path,
            )
        )

        #
        # ============================================================
        # Aplicar alterações de arquivos.
        # ============================================================
        #

        if changes:

            content = (
                self.__apply_changes(
                    content=content,
                    changes=changes,
                )
            )

        #
        # ============================================================
        # Gravar.
        # ============================================================
        #

        aip_path.write_text(
            content,
            encoding="utf-8",
        )

    @staticmethod
    def __replace_version(
        content: str,
        version: str,
    ) -> str:
        """
        Atualiza a propriedade ProductVersion.
        """

        pattern = re.compile(
            r'(<ROW\b'
            r'(?=[^>]*\bProperty\s*=\s*"'
            r'ProductVersion"'
            r')'
            r'[^>]*\bValue\s*=\s*")'
            r'[^"]*'
            r'(")',
            re.IGNORECASE | re.DOTALL,
        )

        def replacement(
            match: re.Match,
        ) -> str:

            return (
                match.group(
                    1,
                )
                + version
                + match.group(
                    2,
                )
            )

        updated_content, count = (
            pattern.subn(
                replacement,
                content,
                count=1,
            )
        )

        if count == 0:

            raise ValueError(
                "ProductVersion não encontrado no AIP."
            )

        return updated_content

    @classmethod
    def __replace_synchronized_folder(
        cls,
        content: str,
        publish_path: Path,
    ) -> str:
        """
        Atualiza somente o SourcePath do componente
        SynchronizedFolderComponent.

        O caminho Windows é gravado com as barras invertidas
        duplicadas, conforme o formato esperado pelo AIP.
        """

        publish_path_text = (
            str(
                publish_path.resolve(),
            )
            .replace(
                "\\",
                "\\\\",
            )
        )

        component_pattern = re.compile(
            r'(?P<header>'
            r'<COMPONENT\b'
            r'(?=[^>]*\bcid\s*=\s*"'
            + re.escape(
                cls.__SYNCHRONIZED_FOLDER_COMPONENT,
            )
            + r'"'
            r')'
            r'[^>]*>'
            r')'
            r'(?P<body>.*?)'
            r'(?P<footer>'
            r'</COMPONENT>'
            r')',
            re.IGNORECASE | re.DOTALL,
        )

        def replace_component(
            match: re.Match,
        ) -> str:

            header = match.group(
                "header",
            )

            body = match.group(
                "body",
            )

            footer = match.group(
                "footer",
            )

            source_pattern = re.compile(
                r'(?P<prefix>'
                r'\bSourcePath\s*=\s*"'
                r')'
                r'(?P<value>[^"]*)'
                r'(?P<suffix>")',
                re.IGNORECASE,
            )

            def replace_source(
                source_match: re.Match,
            ) -> str:

                return (
                    source_match.group(
                        "prefix",
                    )
                    + publish_path_text
                    + source_match.group(
                        "suffix",
                    )
                )

            updated_body, count = (
                source_pattern.subn(
                    replace_source,
                    body,
                    count=1,
                )
            )

            if count == 0:

                raise ValueError(
                    "Pasta sincronizada "
                    "não possui SourcePath."
                )

            return (
                header
                + updated_body
                + footer
            )

        updated_content, count = (
            component_pattern.subn(
                replace_component,
                content,
                count=1,
            )
        )

        if count == 0:

            raise ValueError(
                "pasta sincronizada "
                "não encontrada no AIP."
            )

        return updated_content

    @classmethod
    def __apply_changes(
        cls,
        content: str,
        changes: list[SetupFileSync],
    ) -> str:
        """
        Aplica as alterações de arquivos ao AIP.

        KEEP:
            Não altera o AIP.

        UPDATE:
            Ainda não implementado.

        ADD:
            Adiciona o arquivo ao MsiFilesComponent.

        REMOVE:
            Remove o ROW correspondente ao SourcePath.
        """

        for change in changes:

            if change.action == SetupFileAction.KEEP:

                continue

            if change.action == SetupFileAction.UPDATE:

                continue

            if change.action == SetupFileAction.ADD:

                content = (
                    cls.__add_file(
                        content=content,
                        change=change,
                    )
                )

                continue

            if change.action == SetupFileAction.REMOVE:

                content = (
                    cls.__remove_file(
                        content=content,
                        source_path=change.source_path,
                        name=change.name,
                    )
                )

        return content

    @classmethod
    def __remove_file(
        cls,
        content: str,
        source_path: str,
        name: str | None = None,
    ) -> str:
        """
        Remove uma única ROW do MsiFilesComponent.

        A identidade da entrada é determinada por File + SourcePath.
        Quando name não é informado, SourcePath é usado como fallback.
        """

        normalized_source_path = cls.__normalize_source_path(source_path)
        normalized_name = str(name or "").strip().casefold()

        component_pattern = re.compile(
            r'(?P<header>'
            r'<COMPONENT\b'
            r'(?=[^>]*\bcid\s*=\s*"'
            + re.escape(cls.__MSI_FILES_COMPONENT)
            + r'"'
            r')'
            r'[^>]*>'
            r')'
            r'(?P<body>.*?)'
            r'(?P<footer>'
            r'</COMPONENT>'
            r')',
            re.IGNORECASE | re.DOTALL,
        )

        removed = False

        def replace_component(match: re.Match) -> str:
            nonlocal removed

            header = match.group("header")
            body = match.group("body")
            footer = match.group("footer")

            row_pattern = re.compile(
                r'(?P<row>'
                r'<ROW\b'
                r'(?=[^>]*\bFile\s*=\s*"(?P<file>[^"]*)")'
                r'(?=[^>]*\bSourcePath\s*=\s*"(?P<source>[^"]*)")'
                r'[^>]*/>'
                r')',
                re.IGNORECASE | re.DOTALL,
            )

            def replace_row(row_match: re.Match) -> str:
                nonlocal removed

                if removed:
                    return row_match.group("row")

                current_name = (
                    str(row_match.group("file") or "")
                    .strip()
                    .casefold()
                )

                current_source_path = cls.__normalize_source_path(
                    row_match.group("source")
                )

                if (
                    current_source_path == normalized_source_path
                    and (
                        not normalized_name
                        or current_name == normalized_name
                    )
                ):
                    removed = True
                    return ""

                return row_match.group("row")

            updated_body = row_pattern.sub(
                replace_row,
                body,
            )

            return (
                header
                + updated_body
                + footer
            )

        updated_content = component_pattern.sub(
            replace_component,
            content,
            count=1,
        )

        if not removed:
            identity = (
                f"File='{name}' + SourcePath='{source_path}'"
                if normalized_name
                else f"SourcePath='{source_path}'"
            )

            raise ValueError(
                "Arquivo para remoção não encontrado no AIP: "
                + identity
            )

        return updated_content

    @classmethod
    def __add_file(
        cls,
        content: str,
        change: SetupFileSync,
    ) -> str:
        """
        Adiciona um arquivo individual ao
        MsiFilesComponent.

        O arquivo é identificado pelo source_path.
        """

        source_path = (
            str(
                change.source_path,
            ).strip()
        )

        name = (
            str(
                change.name,
            ).strip()
        )

        if not source_path:

            raise ValueError(
                "Arquivo para adição "
                "não possui SourcePath."
            )

        if not name:

            raise ValueError(
                "Arquivo para adição "
                "não possui nome."
            )

        normalized_source_path = (
            cls.__normalize_source_path(
                source_path,
            )
        )

        component_pattern = re.compile(
            r'(?P<header>'
            r'<COMPONENT\b'
            r'(?=[^>]*\bcid\s*=\s*"'
            + re.escape(
                cls.__MSI_FILES_COMPONENT,
            )
            + r'"'
            r')'
            r'[^>]*>'
            r')'
            r'(?P<body>.*?)'
            r'(?P<footer>'
            r'</COMPONENT>'
            r')',
            re.IGNORECASE | re.DOTALL,
        )

        component_match = (
            component_pattern.search(
                content,
            )
        )

        if component_match is None:

            raise ValueError(
                "MsiFilesComponent "
                "não encontrado no AIP."
            )

        body = component_match.group(
            "body",
        )

        if cls.__contains_file_source_path(
            body=body,
            name=name,
            source_path=normalized_source_path,
        ):

            raise ValueError(
                "Arquivo para adição "
                "já existe no AIP: "
                f"{source_path}"
            )

        component_id = (
            cls.__create_component_id(
                body=body,
                name=name,
            )
        )

        escaped_name = (
            cls.__escape_attribute(
                name,
            )
        )

        escaped_source_path = (
            cls.__escape_attribute(
                source_path,
            )
        )

        new_row = (
            "\n"
            "  <ROW\n"
            f'    File="{escaped_name}"\n'
            f'    Component_="{component_id}"\n'
            f'    SourcePath="{escaped_source_path}"\n'
            "  />\n"
        )

        insertion_position = (
            body.rfind(
                "\n",
            )
        )

        if insertion_position < 0:

            updated_body = (
                body
                + new_row
            )

        else:

            updated_body = (
                body[:insertion_position]
                + new_row
                + body[insertion_position:]
            )

        return (
            content[
                :component_match.start(
                    "body",
                )
            ]
            + updated_body
            + content[
                component_match.end(
                    "body",
                ):
            ]
        )

    @classmethod
    def __contains_file_source_path(
        cls,
        body: str,
        name: str,
        source_path: str,
    ) -> bool:
        """
        Verifica se uma ROW com a combinação
        File + SourcePath já existe no componente.
        """

        normalized_name = (
            str(name or "")
            .strip()
            .casefold()
        )

        normalized_source_path = (
            cls.__normalize_source_path(
                source_path,
            )
        )

        row_pattern = re.compile(
            r'<ROW\b'
            r'(?=[^>]*\bFile\s*=\s*"(?P<file>[^"]*)"'
            r')'
            r'(?=[^>]*\bSourcePath\s*=\s*"(?P<source>[^"]*)"'
            r')'
            r'[^>]*/>',
            re.IGNORECASE | re.DOTALL,
        )

        for match in row_pattern.finditer(body):

            current_name = (
                str(
                    match.group("file") or "",
                )
                .strip()
                .casefold()
            )

            current_source_path = (
                cls.__normalize_source_path(
                    match.group("source"),
                )
            )

            if (
                current_name == normalized_name
                and current_source_path
                == normalized_source_path
            ):
                return True

        return False

    @staticmethod
    def __create_component_id(
        body: str,
        name: str,
    ) -> str:
        """
        Cria um Component_ único para o novo arquivo.

        O nome do arquivo é utilizado como base.
        Quando já existir, um sufixo numérico é acrescentado.
        """

        base = (
            Path(
                name,
            ).name
        )

        base = re.sub(
            r"[^A-Za-z0-9_.-]",
            "_",
            base,
        )

        if not base:

            base = "File"

        existing_pattern = re.compile(
            r'\bComponent_\s*=\s*"'
            r'(?P<component>[^"]*)"'
            r'"?',
            re.IGNORECASE,
        )

        existing_ids = {
            match.group(
                "component",
            ).casefold()
            for match in existing_pattern.finditer(
                body,
            )
        }

        candidate = base

        counter = 1

        while (
            candidate.casefold()
            in existing_ids
        ):

            candidate = (
                f"{base}_{counter}"
            )

            counter += 1

        return candidate

    @staticmethod
    def __escape_attribute(
        value: str,
    ) -> str:
        """
        Escapa caracteres básicos utilizados em atributos
        do AIP.
        """

        return (
            str(value)
            .replace(
                "&",
                "&amp;",
            )
            .replace(
                '"',
                "&quot;",
            )
        )

    @staticmethod
    def __normalize_source_path(
    source_path: str,
    ) -> str:
        """
        Normaliza um SourcePath para comparação.

        São tratados:

            - barras invertidas;
            - barras duplicadas;
            - comparação case-insensitive.
        """

        value = str(
            source_path or "",
        ).strip()

        value = value.replace(
            "\\\\",
            "\\",
        )

        value = value.replace(
            "/",
            "\\",
        )

        value = value.strip(
            "\\",
        )

        return value.casefold()
