"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : vdproj_block_parser.py
Descrição : Localiza blocos estruturais de arquivos .vdproj.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VdprojBlock:
    """
    Representa um bloco estrutural do .vdproj.
    """

    start: int

    end: int

    content: str


class VdprojBlockParser:
    """
    Localiza o bloco estrutural que representa um arquivo
    no projeto Visual Studio Setup.
    """

    def find_file_block(
        self,
        content: str,
        file_name: str,
    ) -> VdprojBlock:
        """
        Localiza o bloco externo do arquivo pelo Name.
        """

        if content is None:
            raise ValueError(
                "Conteúdo do .vdproj não foi informado."
            )

        if not file_name:
            raise ValueError(
                "Nome do arquivo não foi informado."
            )

        name_marker = (
            f'"Name" = "8:{file_name}"'
        )

        name_position = content.find(
            name_marker,
        )

        if name_position < 0:
            raise ValueError(
                "Arquivo não encontrado no .vdproj: "
                f"{file_name}"
            )

        source_marker = (
            f'"SourcePath" = "8:{file_name}"'
        )

        source_position = content.find(
            source_marker,
            name_position,
        )

        if source_position < 0:
            raise ValueError(
                "SourcePath não encontrado para o arquivo: "
                f"{file_name}"
            )

        opening_brace = (
            self.__find_component_opening_brace(
                content=content,
                name_position=name_position,
            )
        )

        closing_brace = (
            self.__find_closing_brace(
                content=content,
                opening_position=opening_brace,
            )
        )

        return VdprojBlock(
            start=opening_brace,
            end=closing_brace + 1,
            content=content[
                opening_brace:
                closing_brace + 1
            ],
        )

    def __find_component_opening_brace(
        self,
        content: str,
        name_position: int,
    ) -> int:
        """
        Localiza a abertura do componente que contém o Name.

        O bloco procurado deve conter tanto o Name quanto,
        posteriormente, o SourcePath.
        """

        candidate_positions: list[int] = []

        position = name_position - 1

        while position >= 0:

            position = content.rfind(
                "{",
                0,
                position + 1,
            )

            if position < 0:
                break

            candidate_positions.append(
                position,
            )

            position -= 1

        for candidate in candidate_positions:

            try:
                closing = (
                    self.__find_closing_brace(
                        content=content,
                        opening_position=candidate,
                    )
                )

            except ValueError:
                continue

            block = content[
                candidate:
                closing + 1
            ]

            if (
                '"SourcePath"' in block
                and '"Folder"' in block
            ):
                return candidate

        raise ValueError(
            "Não foi possível localizar o bloco "
            "do componente do arquivo."
        )

    def __find_closing_brace(
        self,
        content: str,
        opening_position: int,
    ) -> int:
        """
        Localiza o fechamento correspondente ao bloco.
        """

        depth = 0

        for index in range(
            opening_position,
            len(content),
        ):
            character = content[index]

            if character == "{":

                depth += 1

            elif character == "}":

                depth -= 1

                if depth == 0:
                    return index

        raise ValueError(
            "Não foi possível localizar o fim "
            "do bloco do arquivo."
        )