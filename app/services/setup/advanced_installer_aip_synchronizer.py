"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : advanced_installer_aip_synchronizer.py
Descrição : Sincroniza o AIP do Advanced Installer com os
            arquivos reais da pasta de publicação (Release),
            calculando e aplicando KEEP/ADD/REMOVE antes do
            RefreshSync/Build.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.services.setup.advanced_installer_aip_file_comparator import (
    AdvancedInstallerAipFileComparator,
)

from app.services.setup.advanced_installer_aip_file_parser import (
    AdvancedInstallerAipFileParser,
)

from app.services.setup.advanced_installer_aip_modifier import (
    AdvancedInstallerAipModifier,
)


class AdvancedInstallerAipSynchronizer:
    """
    Responsável por sincronizar o AIP com os arquivos reais
    da pasta de publicação antes do RefreshSync/Build.

    O fluxo executado é:

        1. Ler o conteúdo do AIP.
        2. Identificar os arquivos individuais do AIP (Parser).
        3. Comparar com os arquivos reais do Release
           (Comparator), obtendo KEEP/ADD/REMOVE.
        4. Aplicar a versão e as alterações no AIP (Modifier).
    """

    def __init__(
        self,
        parser: AdvancedInstallerAipFileParser,
        comparator: AdvancedInstallerAipFileComparator,
        modifier: AdvancedInstallerAipModifier,
    ) -> None:
        """
        Inicializa o sincronizador.
        """

        if parser is None:

            raise ValueError(
                "AdvancedInstallerAipFileParser "
                "não foi informado."
            )

        if comparator is None:

            raise ValueError(
                "AdvancedInstallerAipFileComparator "
                "não foi informado."
            )

        if modifier is None:

            raise ValueError(
                "AdvancedInstallerAipModifier "
                "não foi informado."
            )

        self.__parser = parser

        self.__comparator = comparator

        self.__modifier = modifier

    def synchronize(
        self,
        aip_path: Path,
        version: str,
        publish_path: Path,
    ) -> None:
        """
        Sincroniza o AIP informado com os arquivos reais
        da pasta de publicação.
        """

        aip_path = Path(
            aip_path,
        )

        publish_path = Path(
            publish_path,
        )

        content = aip_path.read_text(
            encoding="utf-8",
        )

        aip_files = self.__parser.parse(
            content=content,
            publish_path=publish_path,
        )

        changes = self.__comparator.compare(
            aip_files=aip_files,
            publish_path=publish_path,
        )

        self.__modifier.apply(
            aip_path=aip_path,
            version=version,
            publish_path=publish_path,
            changes=changes,
        )
