"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_engine.py
Descrição : Testes do SetupEngine.
--------------------------------------------------------------------
"""

import pytest

from app.models.setup.setup_engine import (
    SetupEngine,
)


def test_deve_possuir_engine_visual_studio():
    """
    Deve possuir o mecanismo Visual Studio.
    """

    assert (
        SetupEngine.VISUAL_STUDIO.value
        == "visual_studio"
    )


def test_deve_possuir_engine_advanced_installer():
    """
    Deve possuir o mecanismo Advanced Installer.
    """

    assert (
        SetupEngine.ADVANCED_INSTALLER.value
        == "advanced_installer"
    )


def test_deve_converter_string_para_setup_engine():
    """
    Deve permitir converter uma configuração
    válida para SetupEngine.
    """

    engine = SetupEngine(
        "visual_studio",
    )

    assert engine == (
        SetupEngine.VISUAL_STUDIO
    )


def test_deve_rejeitar_engine_invalido():
    """
    Deve rejeitar um mecanismo inexistente.
    """

    with pytest.raises(
        ValueError,
    ):
        SetupEngine(
            "setup_inexistente",
        )