"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_factory.py
Descrição : Implementa a Factory responsável pela seleção
            do serviço de geração de Setup.
--------------------------------------------------------------------
"""

from app.abstractions.installer_service import (
    InstallerService,
)

from app.abstractions.setup_factory import (
    SetupFactory,
)

from app.models.setup.setup_engine import (
    SetupEngine,
)


class DefaultSetupFactory(
    SetupFactory,
):
    """
    Implementação padrão da Factory de Setup.

    A Factory recebe os serviços concretos através
    de injeção de dependência.

    Dessa forma ela não conhece os detalhes de criação
    dos serviços.
    """

    def __init__(
        self,
        visual_studio_installer: InstallerService,
        advanced_installer: InstallerService,
    ) -> None:
        """
        Inicializa a Factory.

        Args:
            visual_studio_installer:
                Serviço responsável pela geração de Setup
                através do Visual Studio.

            advanced_installer:
                Serviço responsável pela geração de Setup
                através do Advanced Installer.
        """

        if visual_studio_installer is None:

            raise ValueError(
                "O serviço de instalação do "
                "Visual Studio não foi informado."
            )

        if advanced_installer is None:

            raise ValueError(
                "O serviço de instalação do "
                "Advanced Installer não foi informado."
            )

        self.__visual_studio_installer = (
            visual_studio_installer
        )

        self.__advanced_installer = (
            advanced_installer
        )

    def create(
        self,
        engine: SetupEngine,
    ) -> InstallerService:
        """
        Seleciona o serviço de geração de Setup.

        Args:
            engine:
                Mecanismo de geração solicitado.

        Returns:
            InstallerService correspondente ao mecanismo.

        Raises:
            ValueError:
                Quando o mecanismo não for informado.

            ValueError:
                Quando o mecanismo não for suportado.
        """

        if engine is None:

            raise ValueError(
                "O mecanismo de geração do Setup "
                "não foi informado."
            )

        if engine == SetupEngine.VISUAL_STUDIO:

            return (
                self.__visual_studio_installer
            )

        if engine == SetupEngine.ADVANCED_INSTALLER:

            return (
                self.__advanced_installer
            )

        raise ValueError(
            "Mecanismo de geração de Setup "
            f"não suportado: {engine}"
        )