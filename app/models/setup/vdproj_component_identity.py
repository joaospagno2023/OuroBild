"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : vdproj_component_identity.py
Descrição : Representa a identidade de um componente do .vdproj.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VdprojComponentIdentity:
    """
    Identidade estrutural de um componente do .vdproj.
    """

    guid: str

    identifier: str

    @property
    def key(self) -> str:
        """
        Retorna a chave completa utilizada pelo .vdproj.

        Formato:

        {GUID}:_IDENTIFIER
        """

        return (
            f"{{{self.guid}}}:_"
            f"{self.identifier}"
        )