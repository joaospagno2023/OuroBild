"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_app_settings.py
Descrição : Testes das configurações gerais da aplicação.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.configuration.app_settings import (
    AppSettings,
)

from app.models.configuration.setup_settings import (
    SetupSettings,
)


def create_settings() -> AppSettings:
    """
    Cria uma configuração mínima para os testes.
    """

    return AppSettings(
        application_name="OuroBuild",
        version="1.0.0",
        log_level="INFO",
        base_path=Path(
            r"C:\Custom\OuroBuild",
        ),
        installer_path=Path(
            r"C:\Custom\OuroBuild\Installer",
        ),
        publish_path=Path(
            r"C:\Custom\OuroBuild\Publish",
        ),
        storage={
            "root_path": Path(
                r"C:\Custom\OuroBuild",
            ),
        },
        build_tools={
            "msbuild_path": Path(
                r"C:\Program Files\Microsoft Visual Studio"
                r"\2022\Professional\MSBuild"
                r"\Current\Bin\MSBuild.exe",
            ),
            "advanced_installer_path": Path(
                r"C:\Program Files\Caphyon"
                r"\Advanced Installer 23.7"
                r"\bin\x86\AdvancedInstaller.com",
            ),
            "robocopy_path": Path(
                r"C:\Windows\System32\robocopy.exe",
            ),
        },
        setup=SetupSettings(
            engine="visual_studio",
            output_root=Path(
                r"C:\Setups",
            ),
            aip_root=Path(
                r"C:\AIPProjects",
            ),
        ),
    )


def test_deve_carregar_configuracao_do_setup():
    """
    Deve carregar corretamente a configuração do Setup.
    """

    settings = create_settings()

    assert isinstance(
        settings.setup,
        SetupSettings,
    )

    assert settings.setup.engine == (
        "visual_studio"
    )

    assert settings.setup.aip_root == (
        Path(r"C:\AIPProjects")
    )


def test_deve_permitir_configurar_advanced_installer():
    """
    Deve permitir selecionar Advanced Installer.
    """

    settings = create_settings()

    settings.setup.engine = (
        "advanced_installer"
    )

    assert settings.setup.engine == (
        "advanced_installer"
    )

    assert settings.setup.aip_root == (
        Path(r"C:\AIPProjects")
    )