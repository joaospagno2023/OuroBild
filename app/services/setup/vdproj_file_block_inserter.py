"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : vdproj_file_block_inserter.py
Descrição : Insere blocos de arquivos na estrutura FileSystem
            de projetos .vdproj.
--------------------------------------------------------------------
"""


class VdprojFileBlockInserter:
    """
    Insere blocos de arquivos na estrutura do FileSystem
    de um projeto .vdproj.
    """

    def insert(
        self,
        content: str,
        file_block: str,
    ) -> str:
        """
        Insere um novo bloco de arquivo no FileSystem.
        """

        if content is None:
            raise ValueError(
                "Conteúdo do .vdproj não foi informado."
            )

        if not file_block:
            raise ValueError(
                "Bloco do arquivo não foi informado."
            )

        filesystem_position = (
            self.__find_filesystem_position(
                content,
            )
        )

        return (
            content[:filesystem_position]
            + file_block
            + "\n"
            + content[filesystem_position:]
        )

    @staticmethod
    def __find_filesystem_position(
        content: str,
    ) -> int:
        """
        Localiza a posição onde um novo componente
        deve ser inserido dentro do FileSystem.
        """

        marker = (
            '"DefaultLocation" = '
            '"8:[ProgramFilesFolder]'
        )

        default_location_position = (
            content.find(marker)
        )

        if default_location_position < 0:
            raise ValueError(
                "Estrutura FileSystem não encontrada "
                "no .vdproj."
            )

        filesystem_opening = (
            content.rfind(
                "{",
                0,
                default_location_position,
            )
        )

        if filesystem_opening < 0:
            raise ValueError(
                "Abertura da estrutura FileSystem "
                "não encontrada."
            )

        return filesystem_opening