"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_default_setup_factory.py
Descrição : Testes da Factory responsável pela seleção
            do serviço de geração de Setup.
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


def create_factory():
    """
    Cria uma Factory utilizando serviços simulados.
    """

    visual_studio_installer = MagicMock(
        spec=InstallerService,
    )

    advanced_installer = MagicMock(
        spec=InstallerService,
    )

    factory = DefaultSetupFactory(
        visual_studio_installer=(
            visual_studio_installer
        ),
        advanced_installer=(
            advanced_installer
        ),
    )

    return (
        factory,
        visual_studio_installer,
        advanced_installer,
    )


def test_deve_criar_servico_visual_studio():
    """
    Deve retornar o InstallerService do Visual Studio
    quando o mecanismo selecionado for VISUAL_STUDIO.
    """

    (
        factory,
        visual_studio_installer,
        _,
    ) = create_factory()

    result = factory.create(
        SetupEngine.VISUAL_STUDIO,
    )

    assert result is visual_studio_installer


def test_deve_criar_servico_advanced_installer():
    """
    Deve retornar o InstallerService do Advanced Installer
    quando o mecanismo selecionado for ADVANCED_INSTALLER.
    """

    (
        factory,
        _,
        advanced_installer,
    ) = create_factory()

    result = factory.create(
        SetupEngine.ADVANCED_INSTALLER,
    )

    assert result is advanced_installer


def test_deve_rejeitar_engine_nulo():
    """
    Deve rejeitar um mecanismo não informado.
    """

    factory, _, _ = create_factory()

    with pytest.raises(
        ValueError,
        match="mecanismo de geração do Setup",
    ):
        factory.create(
            None,
        )


def test_deve_rejeitar_servico_visual_studio_nulo():
    """
    Deve rejeitar a criação da Factory sem
    o serviço do Visual Studio.
    """

    advanced_installer = MagicMock(
        spec=InstallerService,
    )

    with pytest.raises(
        ValueError,
        match="serviço de instalação do Visual Studio",
    ):
        DefaultSetupFactory(
            visual_studio_installer=None,
            advanced_installer=(
                advanced_installer
            ),
        )


def test_deve_rejeitar_servico_advanced_installer_nulo():
    """
    Deve rejeitar a criação da Factory sem
    o serviço do Advanced Installer.
    """

    visual_studio_installer = MagicMock(
        spec=InstallerService,
    )

    with pytest.raises(
        ValueError,
        match="serviço de instalação do Advanced Installer",
    ):
        DefaultSetupFactory(
            visual_studio_installer=(
                visual_studio_installer
            ),
            advanced_installer=None,
        )


def test_deve_rejeitar_engine_nao_suportado():
    """
    Deve rejeitar um mecanismo que não seja suportado.
    """

    factory, _, _ = create_factory()

    unsupported_engine = MagicMock(
        name="UNSUPPORTED",
    )

    with pytest.raises(
        ValueError,
        match="Mecanismo de geração de Setup não suportado",
    ):
        factory.create(
            unsupported_engine,
        )