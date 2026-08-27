"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_factory_configuration.py
Descrição : Testes da integração entre AppSettings e SetupFactory.
--------------------------------------------------------------------
"""

from unittest.mock import MagicMock

from app.abstractions.installer_service import (
    InstallerService,
)

from app.models.configuration.app_settings import (
    AppSettings,
)

from app.models.configuration.build_tools_settings import (
    BuildToolsSettings,
)

from app.models.configuration.setup_settings import (
    SetupSettings,
)

from app.models.configuration.storage_settings import (
    StorageSettings,
)

from app.models.setup.setup_engine import (
    SetupEngine,
)

from app.services.setup.setup_factory import (
    DefaultSetupFactory,
)


def create_settings() -> AppSettings:
    """
    Cria uma configuração mínima da aplicação.
    """

    return AppSettings(
        application_name="OuroBuild",
        version="1.0.0",
        log_level="INFO",
        base_path=r"C:\Custom\OuroBuild",
        installer_path=(
            r"C:\Custom\OuroBuild\Installer"
        ),
        publish_path=(
            r"C:\Custom\OuroBuild\Publish"
        ),
        storage=StorageSettings(
            root_path=(
                r"C:\Custom\OuroBuild"
            ),
        ),
        build_tools=BuildToolsSettings(
            msbuild_path=(
                r"C:\Program Files\Microsoft Visual Studio"
                r"\2022\Professional\MSBuild"
                r"\Current\Bin\MSBuild.exe"
            ),
            advanced_installer_path=(
                r"C:\Program Files\Caphyon"
                r"\Advanced Installer 23.7"
                r"\bin\x86\AdvancedInstaller.com"
            ),
            robocopy_path=(
                r"C:\Windows\System32"
                r"\robocopy.exe"
            ),
        ),
        setup=SetupSettings(
            engine=SetupEngine.VISUAL_STUDIO,
            output_root=r"C:\Custom\OuroBuild\Installer",
        ),
    )


def test_deve_utilizar_engine_configurado_no_settings():
    """
    Deve utilizar o SetupEngine definido em AppSettings.
    """

    settings = create_settings()

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

    result = factory.create(
        settings.setup.engine,
    )

    assert result is (
        visual_studio_installer
    )


def test_deve_preservar_setup_engine_no_app_settings():
    """
    Deve preservar o mecanismo de Setup dentro
    da configuração da aplicação.
    """

    settings = create_settings()

    assert settings.setup.engine == (
        SetupEngine.VISUAL_STUDIO
    )