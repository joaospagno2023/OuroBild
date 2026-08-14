"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_factory.py
Descrição : Testes da DefaultSetupFactory.
--------------------------------------------------------------------
"""

from unittest.mock import MagicMock

import pytest

from app.abstractions.installer_service import (
    InstallerService,
)

from app.models.setup.setup_engine import (
    SetupEngine,
)

from app.services.setup.setup_factory import (
    DefaultSetupFactory,
)


def test_deve_criar_servico_visual_studio():
    """
    Deve retornar o InstallerService do Visual Studio
    quando o mecanismo selecionado for VISUAL_STUDIO.
    """

    visual_studio_installer = MagicMock(
        spec=InstallerService,
    )

    factory = DefaultSetupFactory(
        visual_studio_installer=(
            visual_studio_installer
        ),
    )

    result = factory.create(
        SetupEngine.VISUAL_STUDIO,
    )

    assert result is (
        visual_studio_installer
    )


def test_deve_rejeitar_engine_nulo():
    """
    Deve rejeitar um mecanismo não informado.
    """

    visual_studio_installer = MagicMock(
        spec=InstallerService,
    )

    factory = DefaultSetupFactory(
        visual_studio_installer=(
            visual_studio_installer
        ),
    )

    with pytest.raises(
        ValueError,
        match="mecanismo de geração do Setup",
    ):
        factory.create(
            None,
        )


def test_deve_rejeitar_advanced_installer_ainda_nao_implementado():
    """
    Deve informar que Advanced Installer ainda
    não possui implementação.
    """

    visual_studio_installer = MagicMock(
        spec=InstallerService,
    )

    factory = DefaultSetupFactory(
        visual_studio_installer=(
            visual_studio_installer
        ),
    )

    with pytest.raises(
        NotImplementedError,
        match="Advanced Installer",
    ):
        factory.create(
            SetupEngine.ADVANCED_INSTALLER,
        )


def test_deve_rejeitar_servico_visual_studio_nulo():
    """
    Deve rejeitar a criação da Factory sem
    o serviço do Visual Studio.
    """

    with pytest.raises(
        ValueError,
        match="serviço de instalação do Visual Studio",
    ):
        DefaultSetupFactory(
            visual_studio_installer=None,
        )