"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_orchestrator.py
Descrição : Orquestra o processo de geração do Setup.
--------------------------------------------------------------------
"""

from app.models.configuration.app_settings import (
    AppSettings,
)

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.models.setup.setup_result import (
    SetupResult,
)

from app.services.setup.setup_factory import (
    DefaultSetupFactory,
)

from app.services.setup.setup_path_resolver import (
    SetupPathResolver,
)

from app.services.setup.visual_studio_setup_definition_loader import (
    VisualStudioSetupDefinitionLoader,
)

from app.services.workspace.solution_locator_service import (
    SolutionLocatorService,
)

from app.workspace.workspace_resolver import (
    WorkspaceResolver,
)


class DefaultSetupOrchestrator:
    """
    Orquestra a geração de um Setup.

    Responsabilidades:

    - Resolver o Workspace.
    - Resolver os caminhos do Setup.
    - Localizar a Solution.
    - Carregar a definição do Setup.
    - Selecionar o mecanismo configurado.
    - Executar o InstallerService.
    """

    def __init__(
        self,
        workspace_resolver: WorkspaceResolver,
        setup_path_resolver: SetupPathResolver,
        solution_locator: SolutionLocatorService,
        definition_loader: VisualStudioSetupDefinitionLoader,
        setup_factory: DefaultSetupFactory,
        settings: AppSettings,
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

        if solution_locator is None:
            raise ValueError(
                "SolutionLocatorService não foi informado."
            )

        if definition_loader is None:
            raise ValueError(
                "VisualStudioSetupDefinitionLoader "
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

        self.__solution_locator = (
            solution_locator
        )

        self.__definition_loader = (
            definition_loader
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
            # Workspace
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
            # Caminhos
            #

            paths = (
                self.__setup_path_resolver.resolve(
                    project=workspace.project,
                    project_root=(
                        workspace.project_file.parent
                    ),
                    installer_root=(
                        self.__settings.installer_path
                    ),
                )
            )

            #
            # Solution
            #

            solution_path = (
                self.__solution_locator.find_solution(
                    workspace.project_file,
                )
            )

            if solution_path is None:

                return SetupResult(
                    success=False,
                    message=(
                        "Solution não encontrada "
                        f"para o projeto "
                        f"'{request.project_id}'."
                    ),
                    project_id=(
                        request.project_id
                    ),
                    output_msi=(
                        paths.output_msi
                    ),
                )

            #
            # Definição do Setup
            #

            definition = (
                self.__definition_loader.load(
                    setup_project_path=(
                        paths.aip_path
                    ),
                    solution_path=(
                        solution_path
                    ),
                    configuration=(
                        request.configuration
                    ),
                    platform=(
                        workspace.project.platform
                    ),
                )
            )

            #
            # Seleção do Installer
            #

            installer = (
                self.__setup_factory.create(
                    self.__settings.setup.engine,
                )
            )

            #
            # Execução
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