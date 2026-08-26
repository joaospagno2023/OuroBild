"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_orchestrator.py
Descrição : Orquestra o processo de geração do Setup.
--------------------------------------------------------------------
"""

import os

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

from app.services.setup.setup_workspace_service import (
    SetupWorkspaceService,
)

from app.services.setup.temporary_solution_service import (
    TemporarySolutionService,
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
    - Localizar a Solution original.
    - Carregar a definição do Setup.
    - Criar uma cópia temporária do projeto Setup.
    - Preparar somente a cópia temporária.
    - Criar uma Solution temporária.
    - Executar o InstallerService.
    - Limpar o workspace temporário ao final.

    IMPORTANTE:

    O projeto Setup original nunca é substituído.

    A Solution original nunca é modificada.

    Os arquivos originais do TFS permanecem intactos
    durante todo o processo.
    """

    def __init__(
        self,
        workspace_resolver: WorkspaceResolver,
        setup_path_resolver: SetupPathResolver,
        solution_locator: SolutionLocatorService,
        definition_loader: VisualStudioSetupDefinitionLoader,
        setup_factory: DefaultSetupFactory,
        setup_project_preparer: SetupProjectPreparer,
        setup_workspace_service: SetupWorkspaceService,
        settings: AppSettings,
        temporary_solution_service: (
            TemporarySolutionService | None
        ) = None,
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

        if setup_workspace_service is None:
            raise ValueError(
                "SetupWorkspaceService "
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

        self.__setup_workspace_service = (
            setup_workspace_service
        )

        self.__temporary_solution_service = (
            temporary_solution_service
            if temporary_solution_service is not None
            else TemporarySolutionService()
        )

        self.__settings = settings

    def execute(
        self,
        request: SetupRequest,
    ) -> SetupResult:
        """
        Executa a geração do Setup.

        O projeto Setup original nunca é alterado.

        Todo trabalho que modifica o VDPROJ é realizado
        em uma cópia temporária dentro do publish_path.

        Para projetos Visual Studio Setup:

        Original
            ↓
        VDPROJ temporário
            ↓
        Solution temporária
            ↓
        Visual Studio
            ↓
        MSI
        """

        if request is None:
            raise ValueError(
                "SetupRequest não foi informado."
            )

        workspace_root: Path | None = None

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
            # DIAGNÓSTICO DOS CAMINHOS
            #

            self.__print_path_diagnostics(
                title="CAMINHOS RESOLVIDOS",
                paths={
                    "Project Root": (
                        workspace.project_file.parent
                    ),
                    "Workspace Root": (
                        workspace.environment.root_path
                    ),
                    "Publish Path": (
                        paths.publish_path
                    ),
                    "Output MSI": (
                        paths.output_msi
                    ),
                    "Visual Studio Setup": (
                        paths.visualstudio_setup_path
                    ),
                    "AIP": (
                        paths.aip_path
                    ),
                },
            )

            #
            # Solution ORIGINAL
            #
            # A Solution original permanece somente
            # como fonte de leitura.
            #

            solution_path = (
                self.__solution_locator.find_solution(
                    workspace.project_file,
                )
            )

            #
            # DIAGNÓSTICO DA SOLUTION ORIGINAL
            #

            self.__print_path_diagnostics(
                title="SOLUTION ORIGINAL",
                paths={
                    "Solution Original": (
                        solution_path
                    ),
                },
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
            # Projeto Setup ORIGINAL
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
            # DIAGNÓSTICO DO VDPROJ ORIGINAL
            #

            self.__print_path_diagnostics(
                title="SETUP ORIGINAL",
                paths={
                    "Setup Project": (
                        setup_project_path
                    ),
                },
            )

            #
            # Definição do Setup ORIGINAL
            #
            # O VDPROJ original é somente lido
            # neste momento.
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
            # Projeto Visual Studio Setup
            #

            if (
                paths.visualstudio_setup_path
                is not None
            ):

                #
                # O workspace temporário fica no
                # publish_path.
                #

                workspace_root = (
                    Path(paths.publish_path)
                )

                #
                # DIAGNÓSTICO DO WORKSPACE
                #

                self.__print_path_diagnostics(
                    title="WORKSPACE TEMPORÁRIO",
                    paths={
                        "Workspace Root": (
                            workspace_root
                        ),
                    },
                )

                #
                # Localiza uma DLL existente no VDPROJ
                # para servir como template.
                #

                template_file_name = (
                    self.__resolve_template_file_name(
                        setup_project_path=(
                            setup_project_path
                        ),
                    )
                )

                #
                # Cria e prepara a cópia temporária
                # do VDPROJ.
                #
                # O arquivo original nunca é
                # substituído.
                #

                prepared_setup_path = (
                    self.__setup_project_preparer
                    .prepare(
                        setup_project_path=(
                            setup_project_path
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
                # DIAGNÓSTICO DO VDPROJ TEMPORÁRIO
                #

                self.__print_path_diagnostics(
                    title="SETUP TEMPORÁRIO",
                    paths={
                        "Setup Original": (
                            setup_project_path
                        ),
                        "Setup Temporário": (
                            prepared_setup_path
                        ),
                    },
                )

                #
                # A partir deste ponto o Installer
                # deve trabalhar somente com a cópia.
                #

                paths.visualstudio_setup_path = (
                    prepared_setup_path
                )

                #
                # Cria a Solution temporária.
                #
                # A Solution original continua
                # intacta.
                #

                temporary_solution_path = (
                    self.__temporary_solution_service
                    .create(
                        solution_path=(
                            solution_path
                        ),
                        publish_path=(
                            paths.publish_path
                        ),
                        original_setup_project_path=(
                            setup_project_path
                        ),
                        temporary_setup_project_path=(
                            prepared_setup_path
                        ),
                    )
                )

                #
                # DIAGNÓSTICO DA SOLUTION TEMPORÁRIA
                #

                self.__print_path_diagnostics(
                    title="SOLUTION TEMPORÁRIA",
                    paths={
                        "Solution Original": (
                            solution_path
                        ),
                        "Solution Temporária": (
                            temporary_solution_path
                        ),
                        "Setup Original": (
                            setup_project_path
                        ),
                        "Setup Temporário": (
                            prepared_setup_path
                        ),
                        "Publish Path": (
                            paths.publish_path
                        ),
                    },
                )

                #
                # Cria uma nova definição baseada
                # na definição original.
                #
                # Somente os caminhos são alterados.
                #
                # output_msi permanece o mesmo,
                # pois representa o MSI esperado.
                #

                definition = (
                    definition.model_copy(
                        update={
                            "solution_path": (
                                temporary_solution_path
                            ),
                            "setup_project_path": (
                                prepared_setup_path
                            ),
                        },
                    )
                )

                #
                # DIAGNÓSTICO FINAL DA DEFINIÇÃO
                #

                self.__print_path_diagnostics(
                    title="DEFINIÇÃO ENVIADA AO INSTALLER",
                    paths={
                        "Solution": (
                            definition.solution_path
                        ),
                        "Setup Project": (
                            definition.setup_project_path
                        ),
                        "Output MSI": (
                            paths.output_msi
                        ),
                    },
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

        finally:

            #
            # LIMPEZA DO WORKSPACE TEMPORÁRIO
            #
            # Não existe restauração do VDPROJ
            # original porque o original nunca foi
            # alterado.
            #
            # Durante o diagnóstico podemos preservar
            # os arquivos temporários para executar
            # manualmente o mesmo comando do Visual Studio.
            #

            keep_temporary_files = (
                os.getenv(
                    "OUROBUILD_KEEP_TEMPORARY_FILES",
                    "",
                ).strip().lower()
                in {
                    "1",
                    "true",
                    "yes",
                    "sim",
                }
            )

            print()
            print(
                "[OuroBuild] Keep temporary files: "
                f"{keep_temporary_files}"
            )

            if workspace_root is not None:
                try:

                    self.__setup_workspace_service.cleanup(
                        workspace_root=(
                            workspace_root
                        ),
                        keep_temporary_files=(
                            keep_temporary_files
                        ),
                    )

                    if keep_temporary_files:
                        print(
                            "[OuroBuild] Workspace temporário "
                            "preservado para diagnóstico:"
                        )
                        print(
                            "[OuroBuild] "
                            f"{workspace_root}"
                        )

                except Exception:
                    #
                    # A limpeza não deve mascarar
                    # o resultado da geração.
                    #

                    pass

    @staticmethod
    def __print_path_diagnostics(
        title: str,
        paths: dict[str, Path | str | None],
    ) -> None:
        """
        Exibe diagnóstico dos caminhos utilizados
        durante a geração do Setup.

        Esta função existe exclusivamente para
        diagnóstico do problema MAX_PATH.
        """

        print()
        print("=" * 70)
        print(
            "[OuroBuild] "
            f"{title}"
        )
        print("=" * 70)

        longest_path = None
        longest_length = -1

        for name, value in paths.items():

            if value is None:

                print(
                    f"[OuroBuild] {name}: <None>"
                )

                continue

            path_text = str(value)

            path_length = len(
                path_text
            )

            print(
                f"[OuroBuild] {name}:"
            )

            print(
                f"[OuroBuild] {path_text}"
            )

            print(
                f"[OuroBuild] Length: "
                f"{path_length}"
            )

            if path_length > longest_length:

                longest_length = (
                    path_length
                )

                longest_path = (
                    name,
                    path_text,
                )

        print()
        print(
            "[OuroBuild] Windows MAX_PATH:"
        )
        print(
            "[OuroBuild] 260 caracteres"
        )

        print(
            "[OuroBuild] Windows MAX DIRECTORY:"
        )
        print(
            "[OuroBuild] 248 caracteres"
        )

        if longest_path is not None:

            print()

            print(
                "[OuroBuild] MAIOR CAMINHO:"
            )

            print(
                "[OuroBuild] "
                f"{longest_path[0]}"
            )

            print(
                "[OuroBuild] "
                f"{longest_path[1]}"
            )

            print(
                "[OuroBuild] Length:"
            )

            print(
                "[OuroBuild] "
                f"{longest_length}"
            )

        print("=" * 70)

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