"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_file_modifier.py
Descrição : Modifica arquivos de um projeto Visual Studio Setup.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.models.setup.setup_file_sync import (
    SetupFileSync,
)

from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)


class SetupFileModifier:
    """
    Modifica uma cópia de trabalho do .vdproj.

    O arquivo original nunca deve ser alterado por esta classe.
    """

    def __init__(
        self,
        block_parser: VdprojBlockParser | None = None,
    ) -> None:
        """
        Inicializa o modificador.
        """

        self.__block_parser = (
            block_parser
            or VdprojBlockParser()
        )

    def apply(
        self,
        vdproj_path: Path,
        changes: list[SetupFileSync],
    ) -> None:
        """
        Aplica as alterações calculadas ao .vdproj.
        """

        if vdproj_path is None:
            raise ValueError(
                "Caminho do .vdproj não foi informado."
            )

        if changes is None:
            raise ValueError(
                "Alterações não foram informadas."
            )

        vdproj_path = Path(
            vdproj_path,
        )

        if not vdproj_path.exists():
            raise FileNotFoundError(
                "Arquivo .vdproj não encontrado: "
                f"{vdproj_path}"
            )

        content = vdproj_path.read_text(
            encoding="utf-8",
        )

        for change in changes:

            match change.action:

                case SetupFileAction.UPDATE:

                    content = (
                        self.__update_source_path(
                            content=content,
                            change=change,
                        )
                    )

                case SetupFileAction.REMOVE:

                    content = (
                        self.__remove_file(
                            content=content,
                            change=change,
                        )
                    )

                case SetupFileAction.ADD:

                    raise NotImplementedError(
                        "A inclusão de novos arquivos no "
                        ".vdproj ainda não foi implementada."
                    )

        vdproj_path.write_text(
            content,
            encoding="utf-8",
        )

    def __update_source_path(
        self,
        content: str,
        change: SetupFileSync,
    ) -> str:
        """
        Atualiza somente o SourcePath de um arquivo.
        """

        block = (
            self.__block_parser.find_file_block(
                content=content,
                file_name=change.name,
            )
        )

        old_block = block.content

        marker = (
            '"SourcePath" = "8:'
        )

        source_position = (
            old_block.find(marker)
        )

        if source_position < 0:
            raise ValueError(
                "SourcePath não encontrado no bloco do arquivo: "
                f"{change.name}"
            )

        value_start = (
            source_position
            + len(marker)
        )

        value_end = old_block.find(
            '"',
            value_start,
        )

        if value_end < 0:
            raise ValueError(
                "Valor do SourcePath não pôde ser localizado: "
                f"{change.name}"
            )

        new_block = (
            old_block[:value_start]
            + change.source_path
            + old_block[value_end:]
        )

        return (
            content[:block.start]
            + new_block
            + content[block.end:]
        )

    def __remove_file(
        self,
        content: str,
        change: SetupFileSync,
    ) -> str:
        """
        Remove o bloco estrutural completo do arquivo.
        """

        block = (
            self.__block_parser.find_file_block(
                content=content,
                file_name=change.name,
            )
        )

        start = block.start
        end = block.end

        while (
            start > 0
            and content[start - 1]
            in (
                "\r",
                "\n",
                " ",
                "\t",
            )
        ):
            start -= 1

        return (
            content[:start]
            + content[end:]
        )