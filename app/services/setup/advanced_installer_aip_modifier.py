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
                    publish_path=publish_path,
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
        publish_path: Path,
    ) -> str:
        """
        Aplica as alterações de arquivos ao AIP.

        KEEP:
            Mantém o arquivo no Setup e atualiza seu SourcePath
            para a pasta Release atual.

        UPDATE:
            Ainda não implementado.

        ADD:
            Adiciona o arquivo ao MsiFilesComponent.

        REMOVE:
            Remove o ROW correspondente ao SourcePath.
        """

        for change in changes:

            if change.action == SetupFileAction.KEEP:

                content = (
                    cls.__update_file_source_path(
                        content=content,
                        change=change,
                        publish_path=publish_path,
                    )
                )

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
                        aip_file_id=change.aip_file_id,
                    )
                )

        return content

    @classmethod
    def __update_file_source_path(
        cls,
        content: str,
        change: SetupFileSync,
        publish_path: Path,
    ) -> str:
        """
        Atualiza o SourcePath de um arquivo individual existente.

        A identificação da ROW é feita de forma progressiva:

            1. Component_ quando aip_file_id estiver disponível;
            2. caminho relativo do SourcePath (comparado contra a
               parte do SourcePath atual que vem depois de
               "\\bin\\Release\\");
            3. File / FileName, apenas como último recurso, e
               somente quando exatamente uma ROW do componente
               possuir aquele nome (evita atualizar a ROW errada
               quando o mesmo nome de arquivo aparece em vários
               diretórios, como "nfse.xsd" ou
               "xmldsig-core-schema_v1.01.xsd").

        O novo SourcePath é construído preservando o prefixo da
        ROW encontrada (tudo até e incluindo "\\bin\\Release\\"),
        e substituindo apenas a parte final pelo caminho relativo
        atual do arquivo dentro da pasta de publicação. Isso evita
        gravar um SourcePath incompleto/relativo à raiz errada.
        """

        if not change.name:
            raise ValueError(
                "Arquivo para atualização não possui nome."
            )

        if not change.source_path:
            raise ValueError(
                "Arquivo para atualização não possui SourcePath."
            )

        publish_path = Path(
            publish_path,
        ).resolve()

        file_publish_path = Path(
            change.publish_path,
        ).resolve()

        try:
            relative_path = file_publish_path.relative_to(
                publish_path,
            )
        except ValueError as exc:
            raise ValueError(
                "PublishPath do arquivo não pertence à pasta "
                "de publicação informada:\n"
                f"Arquivo: {file_publish_path}\n"
                f"PublishPath: {publish_path}"
            ) from exc

        expected_relative_path = cls.__normalize_source_path(
            relative_path.as_posix(),
        )

        relative_path_windows = str(
            relative_path,
        )

        normalized_name = (
            str(change.name)
            .strip()
            .casefold()
        )

        normalized_aip_file_id = (
            str(change.aip_file_id or "")
            .strip()
            .casefold()
        )

        component_pattern = re.compile(
            r'(?P<header>'
            r'<COMPONENT\b'
            r'(?=[^>]*\bcid\s*=\s*"'
            + re.escape(
                cls.__MSI_FILES_COMPONENT,
            )
            + r'"'
            r')[^>]*>'
            r')'
            r'(?P<body>.*?)'
            r'(?P<footer>'
            r'</COMPONENT>'
            r')',
            re.IGNORECASE | re.DOTALL,
        )

        row_pattern = re.compile(
            r'(?P<row>'
            r'<ROW\b'
            r'(?=[^>]*\bFile\s*=\s*"(?P<file>[^"]*)")'
            r'(?=[^>]*\bComponent_\s*=\s*"(?P<component>[^"]*)")'
            r'(?=[^>]*\bFileName\s*=\s*"(?P<file_name>[^"]*)")?'
            r'(?=[^>]*\bSourcePath\s*=\s*"(?P<source>[^"]*)")'
            r'[^>]*/>'
            r')',
            re.IGNORECASE | re.DOTALL,
        )

        source_pattern = re.compile(
            r'(?P<prefix>'
            r'\bSourcePath\s*=\s*"'
            r')'
            r'(?P<value>[^"]*)'
            r'(?P<suffix>")',
            re.IGNORECASE,
        )

        def normalize_row_source_path(
            source_path: str,
        ) -> str:
            normalized = (
                str(source_path or "")
                .replace("\\", "/")
                .strip()
            )

            lower_normalized = normalized.casefold()

            release_marker = "/bin/release/"

            marker_index = lower_normalized.find(
                release_marker,
            )

            if marker_index >= 0:
                normalized = normalized[
                    marker_index + len(release_marker):
                ]

            return cls.__normalize_source_path(
                normalized,
            )

        def build_new_source_path(
            current_source_path: str,
        ) -> str:
            """
            Preserva o prefixo da ROW atual (até e incluindo
            "\\bin\\Release\\") e troca apenas a parte final
            pelo caminho relativo atual do arquivo.
            """

            normalized_current = str(
                current_source_path or "",
            ).replace(
                "/",
                "\\",
            )

            marker = "\\bin\\Release\\"

            marker_index = (
                normalized_current
                .casefold()
                .find(
                    marker.casefold(),
                )
            )

            if marker_index < 0:
                raise ValueError(
                    "SourcePath atual não contém "
                    "'\\bin\\Release\\' para calcular o "
                    "novo caminho:\n"
                    f"{current_source_path}"
                )

            prefix = normalized_current[
                : marker_index + len(marker)
            ]

            return prefix + relative_path_windows

        #
        # ------------------------------------------------------------
        # Passo 1: varrer o MsiFilesComponent identificando ROWs
        # candidatas por aip_file_id / caminho relativo (critérios
        # não-ambíguos) e, paralelamente, contar quantas ROWs
        # possuem o mesmo nome (para decidir se o fallback por
        # nome pode ser usado com segurança).
        # ------------------------------------------------------------
        #

        component_match = component_pattern.search(
            content,
        )

        if component_match is None:
            raise ValueError(
                "MsiFilesComponent não encontrado no AIP."
            )

        body = component_match.group(
            "body",
        )

        target_row_match = None
        name_matches_count = 0

        for row_match in row_pattern.finditer(body):

            current_name = (
                str(
                    row_match.group("file") or "",
                )
                .strip()
                .casefold()
            )

            current_component = (
                str(
                    row_match.group("component") or "",
                )
                .strip()
                .casefold()
            )

            current_file_name = (
                str(
                    row_match.group("file_name") or "",
                )
                .strip()
            )

            file_name_parts = {
                part.strip().casefold()
                for part in current_file_name.split("|")
                if part.strip()
            }

            matches_aip_file_id = (
                bool(normalized_aip_file_id)
                and current_component
                == normalized_aip_file_id
            )

            matches_relative_source_path = (
                bool(expected_relative_path)
                and normalize_row_source_path(
                    row_match.group("source"),
                )
                == expected_relative_path
            )

            if current_name == normalized_name or (
                normalized_name in file_name_parts
            ):
                name_matches_count += 1

            if target_row_match is not None:
                continue

            if matches_aip_file_id or matches_relative_source_path:
                target_row_match = row_match

        #
        # ------------------------------------------------------------
        # Passo 2: se nada bateu por aip_file_id/caminho relativo,
        # só recorrer ao nome quando ele for inequívoco no
        # componente (exatamente uma ROW com aquele nome).
        # ------------------------------------------------------------
        #

        if target_row_match is None and name_matches_count == 1:

            for row_match in row_pattern.finditer(body):

                current_name = (
                    str(
                        row_match.group("file") or "",
                    )
                    .strip()
                    .casefold()
                )

                current_file_name = (
                    str(
                        row_match.group("file_name") or "",
                    )
                    .strip()
                )

                file_name_parts = {
                    part.strip().casefold()
                    for part in current_file_name.split("|")
                    if part.strip()
                }

                if (
                    current_name == normalized_name
                    or normalized_name in file_name_parts
                ):
                    target_row_match = row_match
                    break

        if target_row_match is None:

            ambiguity_note = (
                " (nome ambíguo: existem "
                f"{name_matches_count} ROWs com esse nome "
                "no AIP; forneça aip_file_id para desambiguar)"
                if name_matches_count > 1
                else ""
            )

            raise ValueError(
                "Arquivo para atualização do SourcePath "
                "não encontrado de forma inequívoca no "
                "MsiFilesComponent do AIP:\n"
                f"File: {change.name}\n"
                f"SourcePath: {change.source_path}\n"
                f"FileId: {change.aip_file_id}\n"
                f"SourcePath esperado no Release: "
                f"{relative_path.as_posix()}"
                + ambiguity_note
            )

        current_row_text = target_row_match.group(
            "row",
        )

        new_source_path = build_new_source_path(
            target_row_match.group("source"),
        )

        escaped_source_path = cls.__escape_attribute(
            new_source_path,
        )

        updated_row_text, count = source_pattern.subn(
            lambda source_match: (
                source_match.group("prefix")
                + escaped_source_path
                + source_match.group("suffix")
            ),
            current_row_text,
            count=1,
        )

        if count == 0:
            raise ValueError(
                "ROW encontrada não possui SourcePath "
                "para atualizar:\n"
                f"{current_row_text}"
            )

        updated_body = (
            body[: target_row_match.start()]
            + updated_row_text
            + body[target_row_match.end():]
        )

        return (
            content[
                : component_match.start(
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
    def __remove_file(
        cls,
        content: str,
        source_path: str,
        name: str | None = None,
        aip_file_id: str | None = None,
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

                normalized_aip_file_id = (
                    str(aip_file_id or "")
                    .strip()
                    .casefold()
                )

                if (
                    normalized_aip_file_id
                    and current_name == normalized_aip_file_id
                ):
                    removed = True
                    return ""

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
                f"FileId='{aip_file_id}'"
                if aip_file_id
                else (
                    f"File='{name}' + SourcePath='{source_path}'"
                    if normalized_name
                    else f"SourcePath='{source_path}'"
                )
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