"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : advanced_installer_aip_modifier.py
Descrição : Prepara um projeto Advanced Installer (.aip) para
            geração de uma nova versão do Setup.
--------------------------------------------------------------------
"""

import re

import uuid

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

    __MSI_DIRS_COMPONENT = (
        "caphyon.advinst.msicomp."
        "MsiDirsComponent"
    )

    __MSI_COMPS_COMPONENT = (
        "caphyon.advinst.msicomp."
        "MsiCompsComponent"
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

        def build_new_source_path() -> str:
            """
            Constrói o novo SourcePath apontando para o arquivo
            físico dentro da pasta de publicação (Release) atual.

            Diferente de uma abordagem que preserva o prefixo
            histórico da ROW (que poderia continuar apontando
            para uma pasta de build antiga, já removida), aqui
            o caminho é montado a partir do PublishPath realmente
            informado, garantindo que o SourcePath sempre reflita
            a localização atual do arquivo.
            """

            return str(
                publish_path / relative_path
            )

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

        new_source_path = build_new_source_path()

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
        Adiciona um arquivo individual ao AIP.

        Diferente de apenas inserir uma ROW no
        MsiFilesComponent, um arquivo novo no MSI
        precisa de:

            1. Um Directory_ válido (MsiDirsComponent),
               criado sob demanda quando a pasta (ex.:
               "arm64", "musl-x64") ainda não existir no
               projeto.

            2. Um Component (MsiCompsComponent) próprio,
               com ComponentId (GUID) único, apontando
               para o Directory_ resolvido.

            3. A ROW do arquivo (MsiFilesComponent),
               referenciando o Component criado e um
               FileName no formato "curto|longo" quando
               o nome não couber no padrão DOS 8.3.

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

        if not change.publish_path:

            raise ValueError(
                "Arquivo para adição "
                "não possui PublishPath."
            )

        normalized_source_path = (
            cls.__normalize_source_path(
                source_path,
            )
        )

        #
        # ------------------------------------------------------------
        # 1. Rejeitar duplicidade.
        # ------------------------------------------------------------
        #

        files_match = cls.__find_component(
            content=content,
            cid=cls.__MSI_FILES_COMPONENT,
            label="MsiFilesComponent",
        )

        if cls.__contains_file_source_path(
            body=files_match.group("body"),
            name=name,
            source_path=normalized_source_path,
        ):

            raise ValueError(
                "Arquivo para adição "
                "já existe no AIP: "
                f"{source_path}"
            )

        #
        # ------------------------------------------------------------
        # 2. Resolver (ou criar) a pasta de destino.
        # ------------------------------------------------------------
        #

        relative_directory = Path(
            source_path,
        ).parent

        content, directory_id = (
            cls.__resolve_or_create_directory(
                content=content,
                relative_directory=relative_directory,
            )
        )

        #
        # ------------------------------------------------------------
        # 3. Criar o Component (MsiCompsComponent).
        # ------------------------------------------------------------
        #

        comps_match = cls.__find_component(
            content=content,
            cid=cls.__MSI_COMPS_COMPONENT,
            label="MsiCompsComponent",
        )

        component_id = (
            cls.__create_unique_attribute_value(
                body=comps_match.group("body"),
                attribute="Component",
                name=name,
            )
        )

        #
        # ------------------------------------------------------------
        # 4. Criar o File (MsiFilesComponent).
        #
        # O corpo é relido pois pode ter sido deslocado
        # pela inserção do diretório no passo anterior.
        # ------------------------------------------------------------
        #

        files_match = cls.__find_component(
            content=content,
            cid=cls.__MSI_FILES_COMPONENT,
            label="MsiFilesComponent",
        )

        files_body = files_match.group(
            "body",
        )

        file_id = (
            cls.__create_file_id(
                body=files_body,
                name=name,
            )
        )

        file_name_attribute = (
            cls.__build_file_name_attribute(
                long_name=name,
                files_body=files_body,
            )
        )

        absolute_source_path = str(
            Path(
                change.publish_path,
            )
        )

        escaped_file_id = cls.__escape_attribute(
            file_id,
        )

        escaped_component_id = cls.__escape_attribute(
            component_id,
        )

        escaped_source_path = cls.__escape_attribute(
            absolute_source_path,
        )

        escaped_file_name = cls.__escape_attribute(
            file_name_attribute,
        )

        component_guid = cls.__create_guid()

        new_component_row = (
            "\n"
            "  <ROW\n"
            f'    Component="{escaped_component_id}"\n'
            f'    ComponentId="{component_guid}"\n'
            f'    Directory_="{directory_id}"\n'
            '    Attributes="0"\n'
            f'    KeyPath="{escaped_file_id}"\n'
            "  />\n"
        )

        content = cls.__insert_row_into_component(
            content=content,
            cid=cls.__MSI_COMPS_COMPONENT,
            new_row=new_component_row,
            label="MsiCompsComponent",
        )

        new_file_row = (
            "\n"
            "  <ROW\n"
            f'    File="{escaped_file_id}"\n'
            f'    Component_="{escaped_component_id}"\n'
            f'    FileName="{escaped_file_name}"\n'
            '    Attributes="0"\n'
            f'    SourcePath="{escaped_source_path}"\n'
            '    SelfReg="false"\n'
            "  />\n"
        )

        content = cls.__insert_row_into_component(
            content=content,
            cid=cls.__MSI_FILES_COMPONENT,
            new_row=new_file_row,
            label="MsiFilesComponent",
        )

        return content

    @classmethod
    def __find_component(
        cls,
        content: str,
        cid: str,
        label: str,
    ) -> re.Match:
        """
        Localiza um bloco <COMPONENT cid="..."> pelo cid
        informado.
        """

        pattern = re.compile(
            r'(?P<header>'
            r'<COMPONENT\b'
            r'(?=[^>]*\bcid\s*=\s*"'
            + re.escape(
                cid,
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

        match = pattern.search(
            content,
        )

        if match is None:

            raise ValueError(
                f"{label} "
                "não encontrado no AIP."
            )

        return match

    @classmethod
    def __insert_row_into_component(
        cls,
        content: str,
        cid: str,
        new_row: str,
        label: str,
    ) -> str:
        """
        Insere uma nova ROW no final do bloco
        <COMPONENT cid="..."> informado.
        """

        match = cls.__find_component(
            content=content,
            cid=cid,
            label=label,
        )

        body = match.group(
            "body",
        )

        insertion_position = body.rfind(
            "\n",
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
                :match.start(
                    "body",
                )
            ]
            + updated_body
            + content[
                match.end(
                    "body",
                ):
            ]
        )

    @classmethod
    def __resolve_or_create_directory(
        cls,
        content: str,
        relative_directory: Path,
    ) -> tuple[str, str]:
        """
        Resolve o Directory_ correspondente à pasta relativa
        informada, criando as ROWs necessárias no
        MsiDirsComponent quando a pasta ainda não existir
        no projeto (ex.: novas arquiteturas de runtime).

        Cada segmento do caminho é resolvido individualmente,
        reaproveitando diretórios já existentes (como
        "x64_Dir"/"x86_Dir") e encadeando novos diretórios a
        partir de "APPDIR".
        """

        parts = [
            part
            for part in relative_directory.parts
            if part not in (
                ".",
                "",
            )
        ]

        parent_id = "APPDIR"

        if not parts:

            return content, parent_id

        dir_row_pattern = re.compile(
            r'<ROW\b'
            r'(?=[^>]*\bDirectory\s*=\s*"(?P<directory>[^"]*)")'
            r'(?=[^>]*\bDirectory_Parent\s*=\s*"(?P<parent>[^"]*)")'
            r'(?=[^>]*\bDefaultDir\s*=\s*"(?P<default_dir>[^"]*)")'
            r'[^>]*/>',
            re.IGNORECASE | re.DOTALL,
        )

        for part in parts:

            match = cls.__find_component(
                content=content,
                cid=cls.__MSI_DIRS_COMPONENT,
                label="MsiDirsComponent",
            )

            body = match.group(
                "body",
            )

            found_id = None

            for row_match in dir_row_pattern.finditer(
                body,
            ):

                if (
                    row_match.group(
                        "parent",
                    ).strip().casefold()
                    == parent_id.casefold()
                    and row_match.group(
                        "default_dir",
                    ).strip().casefold()
                    == part.casefold()
                ):

                    found_id = row_match.group(
                        "directory",
                    ).strip()

                    break

            if found_id is not None:

                parent_id = found_id

                continue

            new_directory_id = (
                cls.__create_unique_attribute_value(
                    body=body,
                    attribute="Directory",
                    name=f"{part}_Dir",
                )
            )

            new_row = (
                "\n"
                "  <ROW\n"
                f'    Directory="'
                f'{cls.__escape_attribute(new_directory_id)}"\n'
                f'    Directory_Parent="'
                f'{cls.__escape_attribute(parent_id)}"\n'
                f'    DefaultDir="'
                f'{cls.__escape_attribute(part)}"\n'
                "  />\n"
            )

            content = cls.__insert_row_into_component(
                content=content,
                cid=cls.__MSI_DIRS_COMPONENT,
                new_row=new_row,
                label="MsiDirsComponent",
            )

            parent_id = new_directory_id

        return content, parent_id

    @staticmethod
    def __create_guid() -> str:
        """
        Cria um novo GUID no formato esperado pelo AIP
        (chaves maiúsculas entre chaves).
        """

        return (
            "{"
            + str(
                uuid.uuid4(),
            ).upper()
            + "}"
        )

    @staticmethod
    def __fits_dos_8_3(
        name: str,
    ) -> bool:
        """
        Verifica se o nome informado já respeita o padrão
        DOS 8.3 (até 8 caracteres de nome + até 3 de
        extensão, sem espaços ou caracteres especiais).
        """

        if not name or " " in name:

            return False

        parts = name.rsplit(
            ".",
            1,
        )

        stem = parts[0]

        extension = (
            parts[1]
            if len(parts) > 1
            else ""
        )

        if not re.fullmatch(
            r"[A-Za-z0-9_\-]{1,8}",
            stem,
        ):

            return False

        if extension and not re.fullmatch(
            r"[A-Za-z0-9_\-]{1,3}",
            extension,
        ):

            return False

        return True

    @staticmethod
    def __create_short_file_name(
        long_name: str,
        existing_short_names: set[str],
    ) -> str:
        """
        Gera um nome curto (DOS 8.3) único para o nome
        informado, evitando colisão com os nomes curtos
        já utilizados no componente.
        """

        parts = long_name.rsplit(
            ".",
            1,
        )

        stem = parts[0]

        extension = (
            parts[1]
            if len(parts) > 1
            else ""
        )

        clean_stem = re.sub(
            r"[^A-Za-z0-9]",
            "",
            stem,
        ).upper()

        if not clean_stem:

            clean_stem = "FILE"

        clean_extension = re.sub(
            r"[^A-Za-z0-9]",
            "",
            extension,
        ).upper()[:3]

        base = clean_stem[:6]

        counter = 1

        while True:

            candidate_stem = (
                f"{base}~{counter}"
            )

            candidate = (
                f"{candidate_stem}.{clean_extension}"
                if clean_extension
                else candidate_stem
            )

            if (
                candidate.casefold()
                not in existing_short_names
            ):

                return candidate

            counter += 1

    @classmethod
    def __build_file_name_attribute(
        cls,
        long_name: str,
        files_body: str,
    ) -> str:
        """
        Constrói o valor do atributo FileName para o novo
        arquivo.

        Quando o nome já respeita o padrão DOS 8.3, o
        próprio nome é utilizado. Caso contrário, é gerado
        um nome curto único no formato "curto|longo",
        conforme utilizado pelo restante do AIP.
        """

        if cls.__fits_dos_8_3(
            long_name,
        ):

            return long_name

        file_name_pattern = re.compile(
            r'\bFileName\s*=\s*"(?P<value>[^"]*)"',
            re.IGNORECASE,
        )

        existing_short_names = set()

        for match in file_name_pattern.finditer(
            files_body,
        ):

            value = match.group(
                "value",
            )

            short_part = (
                value.split(
                    "|",
                    1,
                )[0]
                .strip()
            )

            if short_part:

                existing_short_names.add(
                    short_part.casefold(),
                )

        short_name = (
            cls.__create_short_file_name(
                long_name=long_name,
                existing_short_names=existing_short_names,
            )
        )

        return f"{short_name}|{long_name}"

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
    def __create_unique_attribute_value(
        body: str,
        attribute: str,
        name: str,
    ) -> str:
        """
        Cria um valor único para o atributo informado
        (ex.: "File" ou "Component_") dentro do
        MsiFilesComponent.

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
            r'\b'
            + re.escape(
                attribute,
            )
            + r'\s*=\s*"'
            r'(?P<value>[^"]*)"',
            re.IGNORECASE,
        )

        existing_ids = {
            match.group(
                "value",
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

    @classmethod
    def __create_component_id(
        cls,
        body: str,
        name: str,
    ) -> str:
        """
        Cria um Component_ único para o novo arquivo.
        """

        return cls.__create_unique_attribute_value(
            body=body,
            attribute="Component_",
            name=name,
        )

    @classmethod
    def __create_file_id(
        cls,
        body: str,
        name: str,
    ) -> str:
        """
        Cria um File único para o novo arquivo.

        A tabela File do MSI exige que o valor seja
        único em todo o produto. Como diversos arquivos
        de arquiteturas diferentes (ex.: x86/x64/arm)
        podem possuir o mesmo nome físico, o nome não
        pode ser usado diretamente como chave.
        """

        return cls.__create_unique_attribute_value(
            body=body,
            attribute="File",
            name=name,
        )

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