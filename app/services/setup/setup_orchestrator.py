"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_orchestrator.py
Descrição : Orquestra o processo de geração do Setup.
--------------------------------------------------------------------
"""

from pathlib import Path

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

from app.services.setup.setup_project_preparer import (
    SetupProjectPreparer,
)

from app.services.setup.visual_studio_setup_definition_loader import (
    VisualStudioSetupDefinitionLoader,
)

from app.services.setup.visual_studio_setup_preparer import (
    VisualStudioSetupPreparer,
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
    - Preparar uma cópia do projeto Visual Studio Setup.
    - Preparar uma Solution temporária para utilizar
      o projeto Setup preparado.
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
        setup_project_preparer: SetupProjectPreparer,
        visual_studio_setup_preparer: (
            VisualStudioSetupPreparer
        ),
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

        if setup_project_preparer is None:
            raise ValueError(
                "SetupProjectPreparer "
                "não foi informado."
            )

        if visual_studio_setup_preparer is None:
            raise ValueError(
                "VisualStudioSetupPreparer "
                "não foi informado."
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

        self.__setup_project_preparer = (
            setup_project_preparer
        )

        self.__visual_studio_setup_preparer = (
            visual_studio_setup_preparer
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
                    workspace_root=(
                        workspace.environment.root_path
                    ),
                    installer_root=(
                        self.__settings.setup.output_root
                    ),
                    version=request.version,
                    revision=request.revision,
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
            # Projeto Setup
            #

            setup_project_path = (
                paths.visualstudio_setup_path
                if (
                    paths.visualstudio_setup_path
                    is not None
                )
                else paths.aip_path
            )

            #
            # Definição do Setup
            #

            definition = (
                self.__definition_loader.load(
                    setup_project_path=(
                        setup_project_path
                    ),
                    solution_path=(
                        solution_path
                    ),
                    configuration=(
                        workspace.project.configuration
                    ),
                    platform=(
                        workspace.project.platform
                    ),
                )
            )

            #
            # Preparação do projeto Visual Studio Setup
            #
            # Somente projetos .vdproj passam
            # pela preparação neste momento.
            #

            if (
                paths.visualstudio_setup_path
                is not None
            ):

                #
                # Workspace temporário
                #

                workspace_root = (
                    paths.setup_output_path
                    / ".workspace"
                )

                #
                # Guarda o caminho original
                # do VDPROJ.
                #

                original_setup_project_path = (
                    paths.visualstudio_setup_path
                )

                #
                # Localiza uma DLL existente
                # para utilização como template.
                #

                template_file_name = (
                    self.__resolve_template_file_name(
                        setup_project_path=(
                            original_setup_project_path
                        ),
                    )
                )

                #
                # Prepara uma cópia do VDPROJ.
                #

                prepared_setup_path = (
                    self.__setup_project_preparer
                    .prepare(
                        setup_project_path=(
                            original_setup_project_path
                        ),
                        publish_path=(
                            paths.publish_path
                        ),
                        workspace_root=(
                            workspace_root
                        ),
                        template_file_name=(
                            template_file_name
                        ),
                    )
                )

                #
                # Prepara uma Solution temporária
                # apontando para o VDPROJ preparado.
                #

                prepared_solution_path = (
                    self.__visual_studio_setup_preparer
                    .prepare(
                        solution_path=(
                            solution_path
                        ),
                        original_setup_project_path=(
                            original_setup_project_path
                        ),
                        prepared_setup_project_path=(
                            prepared_setup_path
                        ),
                        workspace_root=(
                            workspace_root
                        ),
                    )
                )

                #
                # O Installer passa a trabalhar
                # com o VDPROJ preparado.
                #

                paths.visualstudio_setup_path = (
                    prepared_setup_path
                )

                #
                # Mantém a definição consistente
                # com o projeto preparado.
                #

                definition.setup_project_path = (
                    prepared_setup_path
                )

                #
                # Mantém a definição consistente
                # com a Solution preparada.
                #

                definition.solution_path = (
                    prepared_solution_path
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

    @staticmethod
    def __resolve_template_file_name(
        setup_project_path: Path,
    ) -> str:
        """
        Localiza uma DLL existente no .vdproj para ser
        utilizada como template de novos arquivos.
        """

        if setup_project_path is None:
            raise ValueError(
                "SetupProjectPath "
                "não foi informado."
            )

        setup_project_path = Path(
            setup_project_path,
        )

        if not setup_project_path.exists():
            raise FileNotFoundError(
                "SetupProjectPath não encontrado: "
                f"{setup_project_path}"
            )

        content = (
            setup_project_path.read_text(
                encoding="utf-8",
            )
        )

        import re

        names = re.findall(
            r'"Name"\s*=\s*"8:([^"]+\.dll)"',
            content,
            flags=re.IGNORECASE,
        )

        if not names:
            raise ValueError(
                "Nenhuma DLL foi encontrada no "
                f"projeto Setup: {setup_project_path}"
            )

        return names[0]