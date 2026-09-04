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
        - remover arquivos individuais obsoletos, incluindo o
          Component e o vínculo de Feature correspondentes;
        - adicionar arquivos individuais novos, incluindo o
          vínculo de Feature necessário para que sejam
          efetivamente instalados;
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

    __MSI_COMPS_COMPONENT = (
        "caphyon.advinst.msicomp."
        "MsiCompsComponent"
    )

    __MSI_FEAT_COMPS_COMPONENT = (
        "caphyon.advinst.msicomp."
        "MsiFeatCompsComponent"
    )

    #
    # Feature padrão utilizada pelos AIPs do OuroBuild.
    #
    # Todas as tabelas FeatureComponents observadas nos
    # projetos existentes utilizam exclusivamente esta
    # Feature.
    #

    __DEFAULT_FEATURE = "MainFeature"

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
            ).replace(
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
            Adiciona o arquivo ao MsiFilesComponent, cria o
            Component correspondente e o vincula à Feature
            padrão do projeto.

        REMOVE:
            Remove o ROW correspondente ao SourcePath, além do
            Component em MsiCompsComponent e do vínculo em
            MsiFeatCompsComponent, evitando que sobrem
            registros órfãos no AIP.
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

        A identidade da ROW é determinada preferencialmente por:

            1. File == aip_file_id;
            2. caminho relativo dentro de bin\\Release.

        FileName é utilizado somente como apoio/fallback.

        Isto é necessário porque no formato AIP:

            File       = identificador interno da ROW;
            FileName   = nome físico do arquivo;
            Component_ = identificador do componente MSI.

        Portanto, aip_file_id NÃO deve ser comparado com Component_.

        O caminho relativo é importante porque o mesmo FileName pode
        existir em diretórios diferentes.
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

        new_source_path = (
            publish_path
            / relative_path
        )

        escaped_source_path = cls.__escape_attribute(
            str(new_source_path),
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

        normalized_relative_path = (
            cls.__normalize_relative_release_path(
                str(relative_path),
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

        row_pattern = re.compile(
            r'(?P<row>'
            r'<ROW\b'
            r'(?=[^>]*\bFile\s*=\s*"'
            r'(?P<file>[^"]*)"'
            r')'
            r'(?=[^>]*\bFileName\s*=\s*"'
            r'(?P<file_name>[^"]*)"'
            r')?'
            r'(?=[^>]*\bSourcePath\s*=\s*"'
            r'(?P<source>[^"]*)"'
            r')'
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

        updated = False

        def replace_component(
            match: re.Match,
        ) -> str:
            nonlocal updated

            header = match.group(
                "header",
            )

            body = match.group(
                "body",
            )

            footer = match.group(
                "footer",
            )

            def replace_row(
                row_match: re.Match,
            ) -> str:
                nonlocal updated

                if updated:
                    return row_match.group(
                        "row",
                    )

                current_file = (
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
                    .casefold()
                )

                current_source_path = (
                    str(
                        row_match.group("source") or "",
                    ).strip()
                )

                current_relative_path = (
                    cls.__normalize_relative_release_path(
                        current_source_path,
                    )
                )

                matches_relative_path = (
                    bool(normalized_relative_path)
                    and current_relative_path
                    == normalized_relative_path
                )

                matches_aip_file_id = (
                    bool(normalized_aip_file_id)
                    and current_file
                    == normalized_aip_file_id
                )

                matches_file_name = (
                    current_file_name
                    == normalized_name
                )

                #
                # Primeiro garante o caminho relativo.
                # Isso impede que um FileName repetido em outra pasta
                # seja atualizado por engano.
                #

                if not matches_relative_path:
                    return row_match.group(
                        "row",
                    )

                #
                # Se temos aip_file_id, ele deve corresponder ao
                # atributo File do AIP.
                #

                if normalized_aip_file_id:

                    if not matches_aip_file_id:
                        return row_match.group(
                            "row",
                        )

                #
                # Sem aip_file_id, usamos FileName como fallback.
                #

                elif not matches_file_name:
                    return row_match.group(
                        "row",
                    )

                updated_row, count = (
                    source_pattern.sub(
                        lambda source_match: (
                            source_match.group("prefix")
                            + escaped_source_path
                            + source_match.group("suffix")
                        ),
                        row_match.group("row"),
                        count=1,
                    ),
                    1,
                )

                if count == 0:
                    return row_match.group(
                        "row",
                    )

                updated = True

                return updated_row

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
        )

        if not updated:
            raise ValueError(
                "Arquivo para atualização do SourcePath "
                "não encontrado em nenhuma MsiFilesComponent "
                "do AIP:\n"
                f"File: {change.name}\n"
                f"SourcePath: {change.source_path}\n"
                f"FileId: {change.aip_file_id}\n"
                f"RelativePath: {normalized_relative_path}"
            )

        return updated_content

    @classmethod
    def __remove_file(
        cls,
        content: str,
        source_path: str,
        name: str | None = None,
        aip_file_id: str | None = None,
    ) -> str:
        """
        Remove uma única ROW do MsiFilesComponent, além do
        Component correspondente em MsiCompsComponent e do
        vínculo de Feature em MsiFeatCompsComponent.

        A identidade da entrada é determinada por File + SourcePath.
        Quando name não é informado, SourcePath é usado como fallback.

        A remoção do Component e do vínculo de Feature é feita a
        partir do identificador Component_ da ROW removida (ou,
        na ausência dele, do próprio File), evitando que registros
        órfãos se acumulem no AIP a cada sincronização. Registros
        órfãos acumulados fazem o RefreshSync do Advanced Installer
        falhar com "row with this key [...] was already registered
        in the table" quando a pasta sincronizada volta a conter um
        arquivo com o mesmo nome.
        """

        normalized_source_path = cls.__normalize_source_path(
            source_path
        )

        normalized_name = (
            str(name or "")
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
        removed_component_id: str | None = None

        def replace_component(
            match: re.Match,
        ) -> str:
            nonlocal removed
            nonlocal removed_component_id

            header = match.group(
                "header",
            )

            body = match.group(
                "body",
            )

            footer = match.group(
                "footer",
            )

            row_pattern = re.compile(
                r'(?P<row>'
                r'<ROW\b'
                r'(?=[^>]*\bFile\s*=\s*"'
                r'(?P<file>[^"]*)"'
                r')'
                r'(?=[^>]*\bComponent_\s*=\s*"'
                r'(?P<component>[^"]*)"'
                r')?'
                r'(?=[^>]*\bSourcePath\s*=\s*"'
                r'(?P<source>[^"]*)"'
                r')'
                r'[^>]*/>'
                r')',
                re.IGNORECASE | re.DOTALL,
            )

            def replace_row(
                row_match: re.Match,
            ) -> str:
                nonlocal removed
                nonlocal removed_component_id

                if removed:
                    return row_match.group(
                        "row",
                    )

                current_name = (
                    str(
                        row_match.group("file") or "",
                    )
                    .strip()
                    .casefold()
                )

                current_component_id = (
                    str(
                        row_match.group("component") or "",
                    )
                    .strip()
                )

                current_source_path = (
                    cls.__normalize_source_path(
                        row_match.group("source")
                    )
                )

                normalized_aip_file_id = (
                    str(aip_file_id or "")
                    .strip()
                    .casefold()
                )

                if (
                    normalized_aip_file_id
                    and current_name
                    == normalized_aip_file_id
                ):
                    removed = True

                    removed_component_id = (
                        current_component_id
                        or row_match.group("file")
                    )

                    return ""

                if (
                    current_source_path
                    == normalized_source_path
                    and (
                        not normalized_name
                        or current_name
                        == normalized_name
                    )
                ):
                    removed = True

                    removed_component_id = (
                        current_component_id
                        or row_match.group("file")
                    )

                    return ""

                return row_match.group(
                    "row",
                )

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
                    f"File='{name}' + "
                    f"SourcePath='{source_path}'"
                    if normalized_name
                    else (
                        f"SourcePath='{source_path}'"
                    )
                )
            )

            raise ValueError(
                "Arquivo para remoção não encontrado no AIP: "
                + identity
            )

        #
        # ============================================================
        # Remove o Component e o vínculo de Feature órfãos.
        #
        # Best-effort: caso as tabelas ou as ROWs correspondentes
        # não existam (AIPs com estrutura diferente), o conteúdo
        # é mantido sem alterações adicionais.
        # ============================================================
        #

        if removed_component_id:

            updated_content = (
                cls.__remove_component(
                    content=updated_content,
                    component_id=removed_component_id,
                )
            )

            updated_content = (
                cls.__remove_feature_component(
                    content=updated_content,
                    component_id=removed_component_id,
                )
            )

        return updated_content

    @classmethod
    def __remove_component(
        cls,
        content: str,
        component_id: str,
    ) -> str:
        """
        Remove a definição de um Component em MsiCompsComponent.

        Best-effort: quando a tabela ou a ROW não existir, o
        conteúdo é retornado sem alterações.
        """

        normalized_target = (
            str(component_id)
            .strip()
            .casefold()
        )

        if not normalized_target:
            return content

        component_pattern = re.compile(
            r'(?P<header>'
            r'<COMPONENT\b'
            r'(?=[^>]*\bcid\s*=\s*"'
            + re.escape(
                cls.__MSI_COMPS_COMPONENT,
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

        row_pattern = re.compile(
            r'<ROW\b'
            r'(?=[^>]*\bComponent\s*=\s*"'
            r'(?P<component>[^"]*)"'
            r')'
            r'[^>]*/>',
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

            def replace_row(
                row_match: re.Match,
            ) -> str:
                current = (
                    str(
                        row_match.group("component") or "",
                    )
                    .strip()
                    .casefold()
                )

                if current == normalized_target:
                    return ""

                return row_match.group(
                    0,
                )

            updated_body = row_pattern.sub(
                replace_row,
                body,
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
            return content

        return updated_content

    @classmethod
    def __remove_feature_component(
        cls,
        content: str,
        component_id: str,
    ) -> str:
        """
        Remove o(s) vínculo(s) de Feature de um Component em
        MsiFeatCompsComponent.

        Um mesmo Component pode, em tese, estar vinculado a mais
        de uma Feature; todas as ocorrências são removidas.

        Best-effort: quando a tabela ou a ROW não existir, o
        conteúdo é retornado sem alterações.
        """

        normalized_target = (
            str(component_id)
            .strip()
            .casefold()
        )

        if not normalized_target:
            return content

        component_pattern = re.compile(
            r'(?P<header>'
            r'<COMPONENT\b'
            r'(?=[^>]*\bcid\s*=\s*"'
            + re.escape(
                cls.__MSI_FEAT_COMPS_COMPONENT,
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

        row_pattern = re.compile(
            r'<ROW\b'
            r'(?=[^>]*\bComponent_\s*=\s*"'
            r'(?P<component>[^"]*)"'
            r')'
            r'[^>]*/>',
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

            def replace_row(
                row_match: re.Match,
            ) -> str:
                current = (
                    str(
                        row_match.group("component") or "",
                    )
                    .strip()
                    .casefold()
                )

                if current == normalized_target:
                    return ""

                return row_match.group(
                    0,
                )

            #
            # Remove todas as ocorrências dentro desta tabela,
            # não somente a primeira.
            #

            updated_body = row_pattern.sub(
                replace_row,
                body,
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
            return content

        return updated_content

    @classmethod
    def __add_file(
        cls,
        content: str,
        change: SetupFileSync,
    ) -> str:
        """
        Adiciona um arquivo individual ao AIP.

        O ADD cria as três referências necessárias:

            1. MsiCompsComponent
            2. MsiFilesComponent
            3. MsiFeatCompsComponent (vínculo com a Feature
               padrão do projeto)

        Sem o vínculo de Feature, o arquivo é adicionado ao MSI
        mas nunca é efetivamente instalado.

        A identificação do COMPONENT é feita pelo atributo cid,
        sem depender da posição dos atributos no XML.
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

        # ============================================================
        # LOCALIZA COMPONENTES DO AIP
        # ============================================================

        component_pattern = re.compile(
            r'(?P<component>'
            r'<COMPONENT\b'
            r'(?=[^>]*\bcid\s*=\s*"'
            r'(?P<cid>[^"]*)"'
            r')'
            r'[^>]*>'
            r'(?P<body>.*?)'
            r'</COMPONENT>'
            r')',
            re.IGNORECASE | re.DOTALL,
        )

        files_component_match = None
        comps_component_match = None
        feat_comps_component_match = None

        for match in component_pattern.finditer(content):
            cid = (
                str(match.group("cid") or "")
                .strip()
                .casefold()
            )

            if cid == cls.__MSI_FILES_COMPONENT.casefold():
                files_component_match = match

            elif cid == cls.__MSI_COMPS_COMPONENT.casefold():
                comps_component_match = match

            elif cid == cls.__MSI_FEAT_COMPS_COMPONENT.casefold():
                feat_comps_component_match = match

        if files_component_match is None:
            raise ValueError(
                "MsiFilesComponent "
                "não encontrado no AIP. "
                "Nenhum COMPONENT com cid "
                f"'{cls.__MSI_FILES_COMPONENT}' foi localizado."
            )

        if comps_component_match is None:
            raise ValueError(
                "MsiCompsComponent "
                "não encontrado no AIP."
            )

        files_body = files_component_match.group(
            "body",
        )

        comps_body = comps_component_match.group(
            "body",
        )

        # ============================================================
        # VERIFICA DUPLICIDADE
        # ============================================================

        if cls.__contains_file_source_path(
            body=files_body,
            name=name,
            source_path=normalized_source_path,
        ):
            raise ValueError(
                "Arquivo para adição "
                "já existe no AIP: "
                f"{source_path}"
            )

        # ============================================================
        # IDENTIFICADOR MSI
        # ============================================================

        component_id = (
            cls.__create_component_id(
                body=files_body,
                name=name,
            )
        )

        escaped_component_id = (
            cls.__escape_attribute(
                component_id,
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

        # ============================================================
        # GUID DO COMPONENT
        # ============================================================

        from uuid import uuid4

        component_guid = (
            "{"
            + str(
                uuid4(),
            ).upper()
            + "}"
        )

        # ============================================================
        # MsiCompsComponent
        # ============================================================

        new_component_row = (
            "\n"
            "  <ROW\n"
            f'    Component="{escaped_component_id}"\n'
            f'    ComponentId="{component_guid}"\n'
            '    Directory_="APPDIR"\n'
            '    Attributes="0"\n'
            f'    KeyPath="{escaped_component_id}"\n'
            "  />\n"
        )

        comps_insertion_position = comps_body.rfind(
            "\n",
        )

        if comps_insertion_position < 0:
            updated_comps_body = (
                comps_body
                + new_component_row
            )
        else:
            updated_comps_body = (
                comps_body[:comps_insertion_position]
                + new_component_row
                + comps_body[comps_insertion_position:]
            )

        content = (
            content[:comps_component_match.start("body")]
            + updated_comps_body
            + content[comps_component_match.end("body"):]
        )

        # ============================================================
        # MsiFilesComponent
        # ============================================================

        # O conteúdo foi alterado acima, então a posição da
        # MsiFilesComponent pode ter mudado. Localizamos novamente.

        files_component_match = None
        feat_comps_component_match = None

        for match in component_pattern.finditer(content):
            cid = (
                str(match.group("cid") or "")
                .strip()
                .casefold()
            )

            if cid == cls.__MSI_FILES_COMPONENT.casefold():
                files_component_match = match

            elif cid == cls.__MSI_FEAT_COMPS_COMPONENT.casefold():
                feat_comps_component_match = match

        if files_component_match is None:
            raise ValueError(
                "MsiFilesComponent "
                "não encontrado no AIP após a criação do Component."
            )

        files_body = files_component_match.group(
            "body",
        )

        new_file_row = (
            "\n"
            "  <ROW\n"
            f'    File="{escaped_component_id}"\n'
            f'    Component_="{escaped_component_id}"\n'
            f'    FileName="{escaped_name}"\n'
            '    Attributes="0"\n'
            f'    SourcePath="{escaped_source_path}"\n'
            '    SelfReg="false"\n'
            "  />\n"
        )

        files_insertion_position = files_body.rfind(
            "\n",
        )

        if files_insertion_position < 0:
            updated_files_body = (
                files_body
                + new_file_row
            )
        else:
            updated_files_body = (
                files_body[:files_insertion_position]
                + new_file_row
                + files_body[files_insertion_position:]
            )

        content = (
            content[:files_component_match.start("body")]
            + updated_files_body
            + content[files_component_match.end("body"):]
        )

        # ============================================================
        # MsiFeatCompsComponent
        #
        # Vincula o novo Component à Feature padrão do projeto.
        # Sem este vínculo, o arquivo nunca seria efetivamente
        # instalado, apesar de existir no MSI.
        #
        # Best-effort: caso o AIP não possua esta tabela, o
        # vínculo é ignorado silenciosamente, preservando o
        # comportamento anterior para esses casos.
        # ============================================================
        #

        if feat_comps_component_match is not None:

            feat_comps_body = (
                feat_comps_component_match.group(
                    "body",
                )
            )

            new_feature_row = (
                "\n"
                "  <ROW\n"
                f'    Feature_="{cls.__DEFAULT_FEATURE}"\n'
                f'    Component_="{escaped_component_id}"\n'
                "  />\n"
            )

            feat_insertion_position = (
                feat_comps_body.rfind(
                    "\n",
                )
            )

            if feat_insertion_position < 0:
                updated_feat_comps_body = (
                    feat_comps_body
                    + new_feature_row
                )
            else:
                updated_feat_comps_body = (
                    feat_comps_body[:feat_insertion_position]
                    + new_feature_row
                    + feat_comps_body[feat_insertion_position:]
                )

            content = (
                content[
                    :feat_comps_component_match.start(
                        "body",
                    )
                ]
                + updated_feat_comps_body
                + content[
                    feat_comps_component_match.end(
                        "body",
                    ):
                ]
            )

        return content

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
            r'(?=[^>]*\bFile\s*=\s*"'
            r'(?P<file>[^"]*)"'
            r')'
            r'(?=[^>]*\bSourcePath\s*=\s*"'
            r'(?P<source>[^"]*)"'
            r')'
            r'[^>]*/>',
            re.IGNORECASE | re.DOTALL,
        )

        for match in row_pattern.finditer(
            body,
        ):

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
        Cria um identificador MSI único e válido.

        O identificador não é o nome físico do arquivo.

        Exemplo:

            protobuf-net.dll
                ->
            protobufnet.dll

        Caracteres não permitidos são removidos.

        Quando o identificador começa com um caractere
        não permitido, é prefixado com "File".
        """

        base = (
            Path(
                name,
            ).name
        )

        #
        # MSI Identifier não deve utilizar hífen.
        #
        # Mantemos letras, números, underscore e ponto.
        #

        base = re.sub(
            r"[^A-Za-z0-9_.]",
            "",
            base,
        )

        if not base:
            base = "File"

        #
        # Identificadores devem começar com letra ou underscore.
        #

        if not re.match(
            r"[A-Za-z_]",
            base,
        ):
            base = (
                "File_"
                + base
            )

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

    @staticmethod
    def __normalize_relative_release_path(
        source_path: str,
    ) -> str:
        """
        Obtém o caminho relativo do arquivo dentro de bin\\Release.

        Exemplo:

            ...\\bin\\Release\\Xml\\Movimento\\Cte\\Schemas\\2.00\\arquivo.xsd

        retorna:

            xml\\movimento\\cte\\schemas\\2.00\\arquivo.xsd

        Quando o caminho já for relativo, ele é apenas normalizado.
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

        normalized = value.casefold()

        marker = "\\bin\\release\\"

        marker_position = normalized.rfind(
            marker,
        )

        if marker_position >= 0:

            relative = normalized[
                marker_position + len(marker):
            ]

            return relative.strip(
                "\\",
            )

        return normalized.strip(
            "\\",
        )