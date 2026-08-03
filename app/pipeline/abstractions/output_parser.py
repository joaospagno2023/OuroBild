"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : output_parser.py
Descrição : Contrato para interpretação da saída de processos.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod
from typing import Any


class OutputParser(ABC):
    """
    Contrato para interpretação da saída de processos.
    """

    @abstractmethod
    def parse(
        self,
        output: str,
        context: Any | None = None,
    ) -> Any:
        """
        Interpreta a saída produzida por um processo.

        Parameters
        ----------
        output:
            Texto retornado pelo processo.

        context:
            Contexto da execução (opcional).

        Returns
        -------
        Resultado estruturado da análise.
        """
        raise NotImplementedError