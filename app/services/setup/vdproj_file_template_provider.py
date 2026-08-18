"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : vdproj_file_template_provider.py
Descrição : Obtém blocos de arquivos utilizados como template
            em projetos .vdproj.
--------------------------------------------------------------------
"""

from app.services.setup.vdproj_block_parser import (
    VdprojBlock,
)

from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)


class VdprojFileTemplateProvider:
    """
    Obtém um bloco de arquivo existente no .vdproj
    para utilização como template.
    """

    def __init__(
        self,
        parser: VdprojBlockParser,
    ) -> None:
        """
        Inicializa o provider.
        """

        if parser is None:
            raise ValueError(
                "VdprojBlockParser não foi informado."
            )

        self.__parser = parser

    def get_template(
        self,
        content: str,
        file_name: str,
    ) -> VdprojBlock:
        """
        Retorna o bloco do arquivo solicitado.
        """

        if content is None:
            raise ValueError(
                "Conteúdo do .vdproj não foi informado."
            )

        if not file_name:
            raise ValueError(
                "Nome do arquivo não foi informado."
            )

        return self.__parser.find_file_block(
            content=content,
            file_name=file_name,
        )