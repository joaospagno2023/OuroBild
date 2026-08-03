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
    Contrato para interpretação da saída de um processo.
    """

    @abstractmethod
    def parse(
        self,
        output: str,
        context: Any | None = None,
    ) -> object:
        """
        Interpreta a saída textual de um processo.

        Parameters
        ----------
        output:
            Saída textual produzida pelo processo.

        context:
            Contexto da execução. Pode conter
            informações adicionais como Request,
            Context ou outros objetos específicos.
        """
        raise NotImplementedError