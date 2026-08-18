"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_file_template_provider.py
Descrição : Obtém um arquivo existente do projeto .vdproj para
            utilização como template de novos arquivos.
--------------------------------------------------------------------
"""

from app.services.setup.vdproj_block_parser import (
    VdprojBlock,
    VdprojBlockParser,
)


class SetupFileTemplateProvider:
    """
    Fornece o bloco estrutural de um arquivo existente
    no projeto .vdproj para ser utilizado como template.
    """

    def __init__(
        self,
        parser: VdprojBlockParser,
    ) -> None:
        """
        Inicializa o Provider.
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
        Localiza e retorna o bloco completo do arquivo
        que será utilizado como template.
        """

        if content is None:
            raise ValueError(
                "Conteúdo do .vdproj não foi informado."
            )

        if not file_name:
            raise ValueError(
                "Nome do arquivo template "
                "não foi informado."
            )

        return self.__parser.find_file_block(
            content=content,
            file_name=file_name,
        )