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

    Fluxo:

        1. Resolve o Workspace.
        2. Valida o Engine.
        3. Resolve os caminhos do Setup.
        4. Carrega a definição do Advanced Installer.
        5. Obtém o InstallerService através da Factory.
        6. Executa a geração do Setup.

    O Orchestrator não possui conhecimento dos detalhes internos
    do Advanced Installer.
    """

    def __init__(
        self,
        workspace_resolver: WorkspaceResolver,
        setup_path_resolver: SetupPathResolver,
        advanced_installer_definition_loader: (
            AdvancedInstallerSetupDefinitionLoader
        ),
        setup_factory: DefaultSetupFactory,
        settings: AppSettings | None = None,
    ) -> None:
        """
        Inicializa o Orchestrator.
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
                    project_id=(
                        request.project_id
                    ),
                    environment_id=(
                        request.environment_id
                    ),
                )
            )

            if workspace is None:

                raise ValueError(
                    "Workspace não foi encontrado "
                    "para o projeto: "
                    f"{request.project_id}"
                )

            #
            # ========================================================
            # Engine
            # ========================================================
            #

            engine = (
                self.__get_engine()
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
                    project=(
                        workspace.project
                    ),
                    project_root=(
                        self.__get_project_root(
                            workspace.project
                        )
                    ),
                    workspace_root=(
                        self.__get_workspace_root(
                            workspace.project
                        )
                    ),
                    installer_root=(
                        self.__get_installer_root()
                    ),
                    aip_root=(
                        self.__get_aip_root(
                            workspace.project
                        )
                    ),
                    version=(
                        request.version
                    ),
                    revision=(
                        request.revision
                    ),
                )
            )

            if paths is None:

                raise ValueError(
                    "SetupPathResolver não retornou "
                    "os caminhos do Setup."
                )

            #
            # ========================================================
            # Definição do Advanced Installer
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

            if definition is None:

                raise ValueError(
                    "AdvancedInstallerSetupDefinitionLoader "
                    "não retornou uma definição de Setup."
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

            if installer is None:

                raise ValueError(
                    "SetupFactory não retornou "
                    "um InstallerService."
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

    def __get_engine(
        self,
    ) -> SetupEngine:
        """
        Obtém o engine configurado.

        Quando AppSettings não foi fornecido, utiliza
        Advanced Installer como padrão.
        """

        if self.__settings is None:

            return SetupEngine.ADVANCED_INSTALLER

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

        return engine

    def __get_project_root(
        self,
        project,
    ) -> Path:
        """
        Obtém a raiz do projeto.
        """

        if getattr(
            project,
            "project_path",
            None,
        ):

            return Path(
                project.project_path,
            ).parent

        if getattr(
            project,
            "publish_path",
            None,
        ):

            return Path(
                project.publish_path,
            ).parent

        return Path.cwd()

    def __get_workspace_root(
        self,
        project,
    ) -> Path:
        """
        Obtém a raiz do Workspace.

        Quando não existe uma estrutura explícita de Workspace,
        utiliza a raiz derivada do projeto.
        """

        if getattr(
            project,
            "project_path",
            None,
        ):

            return Path(
                project.project_path,
            ).parent

        if getattr(
            project,
            "publish_path",
            None,
        ):

            return Path(
                project.publish_path,
            ).parent

        return Path.cwd()

    def __get_installer_root(
        self,
    ) -> Path:
        """
        Obtém a raiz de saída dos instaladores.
        """

        if self.__settings is not None:

            return Path(
                self.__settings.setup.output_root,
            )

        return Path.cwd()

    def __get_aip_root(
        self,
        project,
    ) -> Path:
        """
        Obtém a raiz dos arquivos AIP.
        """

        if self.__settings is not None:

            return Path(
                self.__settings.setup.aip_root,
            )

        if getattr(
            project,
            "aip_path",
            None,
        ):

            return Path(
                project.aip_path,
            ).parent

        return Path.cwd()