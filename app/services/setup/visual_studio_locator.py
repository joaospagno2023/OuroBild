"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : visual_studio_locator.py
Descrição : Localiza o executável do Visual Studio.
--------------------------------------------------------------------
"""

from abc import ABC, abstractmethod
from pathlib import Path


class VisualStudioLocator(ABC):
    """
    Contrato para localização do Visual Studio.
    """

    @abstractmethod
    def locate(self) -> Path:
        """
        Localiza o executável devenv.com.
        """
        raise NotImplementedError