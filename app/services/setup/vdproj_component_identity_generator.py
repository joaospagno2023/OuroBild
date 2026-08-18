"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : vdproj_component_identity_generator.py
Descrição : Gera identidades para componentes do .vdproj.
--------------------------------------------------------------------
"""

import uuid

from app.models.setup.vdproj_component_identity import (
    VdprojComponentIdentity,
)


class VdprojComponentIdentityGenerator:
    """
    Gera identificadores novos para componentes do .vdproj.
    """

    def generate(
        self,
    ) -> VdprojComponentIdentity:
        """
        Gera uma nova identidade.
        """

        guid = str(
            uuid.uuid4()
        ).upper()

        identifier = (
            uuid.uuid4()
            .hex
            .upper()
        )

        return VdprojComponentIdentity(
            guid=guid,
            identifier=identifier,
        )