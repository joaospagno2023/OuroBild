"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_settings.py
Descrição : Testes das configurações utilizadas pelo Setup.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.models.configuration.setup_settings import (
    SetupSettings,
)

from app.models.setup.setup_engine import (
    SetupEngine,
)


def test_deve_criar_setup_settings_com_visual_studio():
    """
    Deve criar a configuração utilizando
    Visual Studio como mecanismo de Setup.
    """

    settings = SetupSettings(
        engine=SetupEngine.VISUAL_STUDIO,
        output_root=Path(
            r"C:\Setups"
        ),
        aip_root=Path(
            r"C:\AIPProjects"
        ),
    )

    assert settings.engine == (
        SetupEngine.VISUAL_STUDIO
    )

    assert settings.output_root == (
        Path(r"C:\Setups")
    )

    assert settings.aip_root == (
        Path(r"C:\AIPProjects")
    )


def test_deve_converter_string_para_setup_engine():
    """
    O Pydantic deve converter a string da configuração
    para o enum SetupEngine.
    """

    settings = SetupSettings(
        engine="visual_studio",
        output_root=Path(
            r"C:\Setups"
        ),
        aip_root=Path(
            r"C:\AIPProjects"
        ),
    )

    assert settings.engine == (
        SetupEngine.VISUAL_STUDIO
    )

    assert settings.output_root == (
        Path(r"C:\Setups")
    )

    assert settings.aip_root == (
        Path(r"C:\AIPProjects")
    )


def test_deve_rejeitar_engine_invalido():
    """
    Deve rejeitar um mecanismo de Setup inválido.
    """

    with pytest.raises(
        ValueError,
    ):
        SetupSettings(
            engine="setup_inexistente",
            output_root=Path(
                r"C:\Setups"
            ),
            aip_root=Path(
                r"C:\AIPProjects"
            ),
        )