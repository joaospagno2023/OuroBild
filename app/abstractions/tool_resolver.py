"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : tool_resolver.py
Descrição : Contrato responsável por resolver ferramentas externas.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod
from pathlib import Path


class ToolResolver(
    ABC,
):
    """
    Resolve o caminho físico de uma ferramenta.
    """

    @abstractmethod
    def resolve(
        self,
        tool_name: str,
    ) -> Path:
        """
        Retorna o caminho absoluto da ferramenta.
        """
        raise NotImplementedError