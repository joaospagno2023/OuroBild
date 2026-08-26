"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : vdproj_file_modifier.py
Descrição : Aplica alterações de arquivos em projetos .vdproj.
--------------------------------------------------------------------
"""

import re

from app.models.setup.setup_file_sync import (
    SetupFileSync,
)

from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)


class VdprojFileModifier:
    """
    Aplica alterações estruturais em um conteúdo .vdproj.
    """

    def __init__(
        self,
        parser: VdprojBlockParser,
    ) -> None:
        """
        Inicializa o Modifier.
        """

        if parser is None:
            raise ValueError(
                "VdprojBlockParser não foi informado."
            )

        self.__parser = parser

    def update(
        self,
        content: str,
        setup_file: SetupFileSync,
    ) -> str:
        """
        Atualiza o bloco de um arquivo existente.
        """

        if content is None:
            raise ValueError(
                "Conteúdo do .vdproj não foi informado."
            )

        if setup_file is None:
            raise ValueError(
                "SetupFileSync não foi informado."
            )

        block = (
            self.__parser.find_file_block(
                content=content,
                file_name=setup_file.name,
            )
        )

        block_content = block.content

        #
        # SourcePath
        #

        block_content = (
            self.__replace_property(
                content=block_content,
                property_name="SourcePath",
                value=setup_file.source_path,
            )
        )

        #
        # AssemblyAsmDisplayName
        #

        if setup_file.assembly_display_name:

            block_content = (
                self.__replace_property(
                    content=block_content,
                    property_name=(
                        "AssemblyAsmDisplayName"
                    ),
                    value=(
                        setup_file.assembly_display_name
                    ),
                )
            )

        return (
            content[:block.start]
            + block_content
            + content[block.end:]
        )

    def remove(
        self,
        content: str,
        setup_file: SetupFileSync,
    ) -> str:
        """
        Remove do .vdproj todos os blocos do arquivo.

        Quando o mesmo arquivo aparece mais de uma vez
        no .vdproj, todas as ocorrências são removidas.
        """

        if content is None:
            raise ValueError(
                "Conteúdo do .vdproj não foi informado."
            )

        if setup_file is None:
            raise ValueError(
                "SetupFileSync não foi informado."
            )

        result = content

        while True:

            try:

                block = (
                    self.__parser.find_file_block(
                        content=result,
                        file_name=setup_file.name,
                    )
                )

            except ValueError as error:

                message = str(error)

                if (
                    message
                    == (
                        "Arquivo não encontrado no .vdproj: "
                        f"{setup_file.name}"
                    )
                ):
                    break

                raise

            #
            # O parser informa o início do bloco
            # estrutural no caractere "{". Porém,
            # a chave do componente fica na linha
            # imediatamente anterior.
            #
            # Exemplo:
            #
            # "{GUID}:_IDENTITY"
            # {
            #     ...
            # }
            #
            # Precisamos remover desde o início
            # da linha da chave, e não somente
            # a partir do "{", para não deixar
            # uma chave órfã no .vdproj.
            #

            line_start = result.rfind(
                "\n",
                0,
                block.start,
            )

            if line_start == -1:
                line_start = 0

            else:
                line_start += 1

            #
            # Remove o bloco completo, incluindo
            # a linha da chave do componente.
            #

            result = (
                result[:line_start]
                + result[block.end:]
            )

        return result

    @staticmethod
    def __replace_property(
        content: str,
        property_name: str,
        value: str,
    ) -> str:
        """
        Substitui uma propriedade do .vdproj.
        """

        pattern = (
            rf'("{re.escape(property_name)}"\s*=\s*"8:)[^"]*(")'
        )

        return re.sub(
            pattern,
            lambda match: (
                match.group(1)
                + value
                + match.group(2)
            ),
            content,
            count=1,
        )