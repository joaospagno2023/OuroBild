"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_factory.py
Descrição : Implementação da Factory responsável pela seleção
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
    ) -> None:
        """
        Inicializa a Factory.

        Args:
            visual_studio_installer:
                Serviço responsável pela geração de Setup
                através do Visual Studio.
        """

        if visual_studio_installer is None:
            raise ValueError(
                "O serviço de instalação do "
                "Visual Studio não foi informado."
            )

        self.__visual_studio_installer = (
            visual_studio_installer
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

            NotImplementedError:
                Quando o mecanismo ainda não possuir
                implementação.
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

            raise NotImplementedError(
                "O mecanismo Advanced Installer "
                "ainda não possui implementação."
            )

        raise ValueError(
            "Mecanismo de geração de Setup "
            f"não suportado: {engine}"
        )