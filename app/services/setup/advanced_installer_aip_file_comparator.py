"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : advanced_installer_aip_file_comparator.py
Descrição : Compara arquivos individuais de um projeto Advanced
            Installer com os arquivos existentes no diretório
            de publicação.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.setup.setup_file import (
    SetupFile,
)

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.models.setup.setup_file_sync import (
    SetupFileSync,
)


class AdvancedInstallerAipFileComparator:
    """
    Compara os arquivos individuais existentes no AIP com
    os arquivos disponíveis no diretório de publicação.

    Esta classe é somente de análise.

    Ela NÃO altera:

        - AIP
        - arquivos
        - diretórios
        - componentes do instalador
    """

    __RELEASE_MARKERS = (
        "/bin/release/",
        "\\bin\\release\\",
    )

    def compare(
        self,
        aip_files: list[SetupFile],
        publish_path: Path,
    ) -> list[SetupFileSync]:
        """
        Compara os arquivos do AIP com o diretório de publicação.
        """

        if aip_files is None:

            raise ValueError(
                "Os arquivos do AIP não foram informados."
            )

        if publish_path is None:

            raise ValueError(
                "PublishPath não foi informado."
            )

        publish_path = Path(
            publish_path,
        )

        if not publish_path.exists():

            raise FileNotFoundError(
                "PublishPath não encontrado:\n"
                f"{publish_path}"
            )

        if not publish_path.is_dir():

            raise ValueError(
                "PublishPath não é um diretório:\n"
                f"{publish_path}"
            )

        #
        # ============================================================
        # Arquivos físicos existentes no Release.
        # ============================================================
        #

        publish_files = (
            self.__load_publish_files(
                publish_path,
            )
        )

        #
        # ============================================================
        # Arquivos individuais existentes no AIP.
        # ============================================================
        #

        aip_index: dict[
            str,
            SetupFile,
        ] = {}

        for setup_file in aip_files:

            key = (
                self.__get_file_identity(
                    setup_file=setup_file,
                    publish_path=publish_path,
                )
            )

            if not key:

                continue

            #
            # --------------------------------------------------------
            # Preservar a primeira ocorrência.
            # --------------------------------------------------------
            #

            if key in aip_index:

                continue

            aip_index[key] = setup_file

        results: list[SetupFileSync] = []

        #
        # ============================================================
        # Arquivos existentes no AIP.
        # ============================================================
        #

        for key, setup_file in aip_index.items():

            publish_file = (
                publish_files.get(
                    key,
                )
            )

            if publish_file is None:

                results.append(
                    self.__create_sync(
                        setup_file=setup_file,
                        action=SetupFileAction.REMOVE,
                    )
                )

                continue

            results.append(
                self.__create_sync(
                    setup_file=setup_file,
                    action=SetupFileAction.KEEP,
                )
            )

        #
        # ============================================================
        # Arquivos novos no Release.
        # ============================================================
        #

        for key, publish_file in publish_files.items():

            if key in aip_index:

                continue

            setup_file = (
                self.__create_setup_file(
                    publish_file=publish_file,
                    publish_path=publish_path,
                )
            )

            results.append(
                self.__create_sync(
                    setup_file=setup_file,
                    action=SetupFileAction.ADD,
                )
            )

        return results

    @classmethod
    def __load_publish_files(
        cls,
        publish_path: Path,
    ) -> dict[str, Path]:
        """
        Carrega todos os arquivos físicos do Release.

        A identidade é baseada no caminho relativo ao Release.
        """

        files: dict[str, Path] = {}

        for file_path in publish_path.rglob("*"):

            if not file_path.is_file():

                continue

            relative_path = (
                file_path.relative_to(
                    publish_path,
                )
            )

            key = (
                cls.__normalize_key(
                    relative_path.as_posix(),
                )
            )

            files[key] = file_path

        return files

    @classmethod
    def __get_file_identity(
        cls,
        setup_file: SetupFile,
        publish_path: Path,
    ) -> str:
        """
        Determina a identidade lógica de um arquivo.

        A identidade NÃO deve depender do caminho histórico
        absoluto armazenado no AIP.

        Exemplos:

            ...\\Versoes\\10.4\\...\\bin\\Release\\ADODB.dll
                ->
            adodb.dll

            ...\\Versoes\\10.4\\...\\bin\\Release\\x64\\foo.dll
                ->
            x64/foo.dll

            x64\\foo.dll
                ->
            x64/foo.dll
        """

        source_path = str(
            setup_file.source_path,
        )

        #
        # ------------------------------------------------------------
        # Normalizar separadores.
        # ------------------------------------------------------------
        #

        normalized = (
            source_path
            .replace(
                "\\",
                "/",
            )
        )

        normalized = (
            normalized
            .strip()
        )

        #
        # ------------------------------------------------------------
        # Caminho absoluto contendo bin/Release.
        #
        # Neste cenário ignoramos todo o caminho histórico anterior
        # ao diretório Release.
        # ------------------------------------------------------------
        #

        release_marker = (
            "/bin/release/"
        )

        lower_path = (
            normalized.lower()
        )

        marker_index = (
            lower_path.find(
                release_marker,
            )
        )

        if marker_index >= 0:

            relative_path = (
                normalized[
                    marker_index
                    + len(release_marker):
                ]
            )

            return cls.__normalize_key(
                relative_path,
            )

        #
        # ------------------------------------------------------------
        # Caso o SourcePath seja relativo.
        # ------------------------------------------------------------
        #

        path = Path(
            normalized,
        )

        if not path.is_absolute():

            return cls.__normalize_key(
                normalized,
            )

        #
        # ------------------------------------------------------------
        # Caminho absoluto abaixo do PublishPath atual.
        # ------------------------------------------------------------
        #

        try:

            relative_path = (
                path.relative_to(
                    publish_path,
                )
            )

            return cls.__normalize_key(
                relative_path.as_posix(),
            )

        except ValueError:

            pass

        #
        # ------------------------------------------------------------
        # Último recurso.
        #
        # Para caminhos absolutos que não conseguimos relacionar
        # ao Release, usamos somente o nome do arquivo.
        # ------------------------------------------------------------
        #

        return cls.__normalize_key(
            path.name,
        )

    @classmethod
    def __create_setup_file(
        cls,
        publish_file: Path,
        publish_path: Path,
    ) -> SetupFile:
        """
        Cria um SetupFile para um arquivo existente no Release
        mas ausente no AIP.
        """

        relative_path = (
            publish_file.relative_to(
                publish_path,
            )
        )

        return SetupFile(
            name=publish_file.name,
            source_path=relative_path.as_posix(),
            publish_path=publish_file,
        )

    @classmethod
    def __create_sync(
        cls,
        setup_file: SetupFile,
        action: SetupFileAction,
    ) -> SetupFileSync:
        """
        Cria o resultado da sincronização preservando os dados
        do SetupFile original.
        """

        return SetupFileSync(
            name=setup_file.name,
            source_path=setup_file.source_path,
            publish_path=setup_file.publish_path,
            assembly_display_name=(
                setup_file.assembly_display_name
            ),
            action=action,
        )

    @staticmethod
    def __normalize_key(
        value: str | Path,
    ) -> str:
        """
        Normaliza uma identidade de arquivo.

        A comparação é:

            - case-insensitive
            - independente do separador de diretórios
            - sem ./ inicial
        """

        return (
            str(value)
            .replace(
                "\\",
                "/",
            )
            .strip()
            .lstrip("./")
            .lower()
        )