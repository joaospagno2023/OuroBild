"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_identity.py
Descrição : Testes do SetupIdentity.
--------------------------------------------------------------------
"""

from uuid import UUID

import pytest

from app.models.setup.setup_identity import (
    SetupIdentity,
)


def test_deve_criar_setup_identity():
    """
    Deve criar uma identidade de Setup válida.
    """

    identity = SetupIdentity(
        product_code=UUID(
            "AEBC9B6C-EEEE-4EBD-8A87-237BE1CFE35B"
        ),
        package_code=UUID(
            "DE04132E-4A07-43E0-B831-70A08E64B18E"
        ),
        upgrade_code=UUID(
            "4182CBF9-1C01-4A2F-BFD8-D909C2BC7FF2"
        ),
    )

    assert identity.product_code == UUID(
        "AEBC9B6C-EEEE-4EBD-8A87-237BE1CFE35B"
    )

    assert identity.package_code == UUID(
        "DE04132E-4A07-43E0-B831-70A08E64B18E"
    )

    assert identity.upgrade_code == UUID(
        "4182CBF9-1C01-4A2F-BFD8-D909C2BC7FF2"
    )


def test_deve_rejeitar_product_code_invalido():
    """
    Deve rejeitar ProductCode inválido.
    """

    with pytest.raises(ValueError):

        SetupIdentity(
            product_code="INVALIDO",
            package_code=(
                "DE04132E-4A07-43E0-B831-70A08E64B18E"
            ),
            upgrade_code=(
                "4182CBF9-1C01-4A2F-BFD8-D909C2BC7FF2"
            ),
        )