"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_vdproj_component_identity_generator.py
Descrição : Testes do VdprojComponentIdentityGenerator.
--------------------------------------------------------------------
"""

import re

from app.services.setup.vdproj_component_identity_generator import (
    VdprojComponentIdentityGenerator,
)


def test_deve_gerar_identidade():
    """
    Deve gerar uma identidade válida.
    """

    generator = (
        VdprojComponentIdentityGenerator()
    )

    result = generator.generate()

    assert result.guid

    assert result.identifier

    assert re.fullmatch(
        r"[A-F0-9-]{36}",
        result.guid,
    )

    assert re.fullmatch(
        r"[A-F0-9]{32}",
        result.identifier,
    )


def test_deve_gerar_chave_no_formato_do_vdproj():
    """
    Deve gerar a chave no formato utilizado pelo .vdproj.
    """

    generator = (
        VdprojComponentIdentityGenerator()
    )

    result = generator.generate()

    assert result.key.startswith(
        f"{{{result.guid}}}:_"
    )

    assert result.key == (
        f"{{{result.guid}}}:_{result.identifier}"
    )


def test_deve_gerar_identidades_diferentes():
    """
    Deve gerar identidades diferentes a cada chamada.
    """

    generator = (
        VdprojComponentIdentityGenerator()
    )

    first = generator.generate()

    second = generator.generate()

    assert first != second

    assert first.key != second.key