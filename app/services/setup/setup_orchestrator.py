"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_orchestrator.py
Descrição : Orquestra o processo de geração do Setup através
            exclusivamente do Advanced Installer.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.configuration.app_settings import (
    AppSettings,
)

from app.models.setup.setup_engine import (
    SetupEngine,
)

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.models.setup.setup_result import (
    SetupResult,
)

from app.services.setup.advanced_installer_setup_definition_loader import (
    AdvancedInstallerSetupDefinitionLoader,
)

from app.services.setup.setup_factory import (
    DefaultSetupFactory,
)

from app.services.setup.setup_path_resolver import (
    SetupPathResolver,
)

from app.workspace.workspace_resolver import (
    WorkspaceResolver,
)


class DefaultSetupOrchestrator:
    """
    Orquestra a geração de Setup através do Advanced Installer.

    O fluxo é intencionalmente simples:

        - Resolver o Workspace.
        - Obter o mecanismo configurado.
        - Resolver os caminhos do Setup.
        - Carregar a definição do AIP.
        - Selecionar o Installer.
        - Executar o InstallerService.

    O Orchestrator não conhece detalhes internos do
    Advanced Installer. Essas responsabilidades permanecem
    nos serviços especializados.
    """

    def __init__(
        self,
        workspace_resolver: WorkspaceResolver,
        setup_path_resolver: SetupPathResolver,
        advanced_installer_definition_loader: (
            AdvancedInstallerSetupDefinitionLoader
        ),
        setup_factory: DefaultSetupFactory,
        settings: AppSettings,
    ) -> None:
        """
        Inicializa o Orchestrator.

        Args:
            workspace_resolver:
                Resolve o Workspace do projeto.

            setup_path_resolver:
                Resolve os caminhos necessários para o Setup.

            advanced_installer_definition_loader:
                Carrega a definição do projeto Advanced Installer.

            setup_factory:
                Seleciona o InstallerService.

            settings:
                Configurações da aplicação.
        """

        if workspace_resolver is None:

            raise ValueError(
                "WorkspaceResolver não foi informado."
            )

        if setup_path_resolver is None:

            raise ValueError(
                "SetupPathResolver não foi informado."
            )

        if advanced_installer_definition_loader is None:

            raise ValueError(
                "AdvancedInstallerSetupDefinitionLoader "
                "não foi informado."
            )

        if setup_factory is None:

            raise ValueError(
                "SetupFactory não foi informado."
            )

        if settings is None:

            raise ValueError(
                "AppSettings não foi informado."
            )

        self.__workspace_resolver = (
            workspace_resolver
        )

        self.__setup_path_resolver = (
            setup_path_resolver
        )

        self.__advanced_installer_definition_loader = (
            advanced_installer_definition_loader
        )

        self.__setup_factory = (
            setup_factory
        )

        self.__settings = settings

    def execute(
        self,
        request: SetupRequest,
    ) -> SetupResult:
        """
        Executa a geração do Setup.

        O engine deve ser Advanced Installer. Qualquer
        configuração diferente é rejeitada explicitamente.
        """

        if request is None:

            raise ValueError(
                "SetupRequest não foi informado."
            )

        try:

            #
            # ========================================================
            # Workspace
            # ========================================================
            #

            workspace = (
                self.__workspace_resolver.resolve(
                    project_id=request.project_id,
                    environment_id=(
                        request.environment_id
                    ),
                )
            )

            #
            # ========================================================
            # Engine
            # ========================================================
            #

            engine = (
                self.__settings.setup.engine
            )

            if isinstance(
                engine,
                str,
            ):

                engine = SetupEngine(
                    engine,
                )

            if engine != SetupEngine.ADVANCED_INSTALLER:

                raise ValueError(
                    "O OuroBuild utiliza exclusivamente "
                    "o Advanced Installer para geração "
                    f"de Setup. Engine configurado: {engine}"
                )

            #
            # ========================================================
            # Caminhos
            # ========================================================
            #

            paths = (
                self.__setup_path_resolver.resolve(
                    project=workspace.project,
                    project_root=(
                        workspace.project_file.parent
                    ),
                    workspace_root=(
                        workspace.environment.root_path
                    ),
                    installer_root=(
                        self.__settings.setup.output_root
                    ),
                    aip_root=(
                        self.__settings.setup.aip_root
                    ),
                    version=request.version,
                    revision=request.revision,
                )
            )

            #
            # ========================================================
            # Advanced Installer
            # ========================================================
            #

            definition = (
                self.__advanced_installer_definition_loader.load(
                    aip_path=(
                        paths.aip_path
                    ),
                    project_id=(
                        request.project_id
                    ),
                    configuration=(
                        workspace.project.configuration
                    ),
                    platform=(
                        workspace.project.platform
                    ),
                    output_msi=(
                        paths.output_msi
                    ),
                )
            )

            #
            # ========================================================
            # Installer
            # ========================================================
            #

            installer = (
                self.__setup_factory.create(
                    SetupEngine.ADVANCED_INSTALLER,
                )
            )

            #
            # ========================================================
            # Execução
            # ========================================================
            #

            return installer.install(
                request=request,
                definition=definition,
                paths=paths,
            )

        except Exception as exception:

            return SetupResult(
                success=False,
                message=(
                    "Erro durante a geração do Setup: "
                    f"{exception}"
                ),
                project_id=(
                    request.project_id
                ),
            )
