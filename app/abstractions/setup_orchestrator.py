"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_orchestrator.py
DescriÃ§Ã£o : Orquestra o processo de geraÃ§Ã£o do Setup atravÃ©s
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

from app.models.build.build_request import (
    BuildRequest,
)

from app.use_cases.execute_build_use_case import (
    ExecuteBuildUseCase,
)

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.models.setup.setup_result import (
    SetupResult,
)

from app.models.pipeline.step_result import (
    StepResult,
)
from app.models.pipeline.step_status import (
    StepStatus,
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
    Orquestra a geraÃ§Ã£o de Setup atravÃ©s do Advanced Installer.

    Fluxo:

        1. Resolve o Workspace.
        2. Valida o Engine.
        3. Executa o Build completo do projeto, quando configurado.
        4. Resolve os caminhos do Setup.
        5. Carrega a definiÃ§Ã£o do Advanced Installer.
        6. ObtÃ©m o InstallerService atravÃ©s da Factory.
        7. Executa a geraÃ§Ã£o do Setup.

    O Orchestrator nÃ£o possui conhecimento dos detalhes internos
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
        execute_build_use_case: ExecuteBuildUseCase | None = None,
        settings: AppSettings | None = None,
    ) -> None:
        """
        Inicializa o Orchestrator.
        """

        if workspace_resolver is None:

            raise ValueError(
                "WorkspaceResolver nÃ£o foi informado."
            )

        if setup_path_resolver is None:

            raise ValueError(
                "SetupPathResolver nÃ£o foi informado."
            )

        if advanced_installer_definition_loader is None:

            raise ValueError(
                "AdvancedInstallerSetupDefinitionLoader "
                "nÃ£o foi informado."
            )

        if setup_factory is None:

            raise ValueError(
                "SetupFactory nÃ£o foi informado."
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

        self.__execute_build_use_case = (
            execute_build_use_case
        )

        self.__settings = settings

    def execute(
        self,
        request: SetupRequest,
    ) -> SetupResult:
        """
        Executa a geraÃ§Ã£o do Setup.
        """

        if request is None:

            raise ValueError(
                "SetupRequest nÃ£o foi informado."
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
                    "Workspace nÃ£o foi encontrado "
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
                    "o Advanced Installer para geraÃ§Ã£o "
                    f"de Setup. Engine configurado: {engine}"
                )

            #
            # ========================================================
            # Build do projeto
            # ========================================================
            #

            if (
                request.run_build
                and self.__execute_build_use_case is not None
            ):

                build_request = BuildRequest(
                    project_id=request.project_id,
                    environment_id=request.environment_id,
                    version=request.version,
                    revision=request.revision,
                )

                build_result = (
                    self.__execute_build_use_case.execute(
                        build_request,
                    )
                )

                if not build_result.success:

                    failed_step = (
                        build_result.failed_step
                        or "Build"
                    )

                    message = (
                        "Falha durante o Build do projeto. "
                        f"Etapa: {failed_step}. "
                        f"{build_result.message}"
                    ).strip()

                    return SetupResult(
                        success=False,
                        message=message,
                        project_id=request.project_id,
                        output_msi=None,
                        duration_seconds=(
                            build_result.elapsed_seconds
                        ),
                        steps=list(build_result.steps),
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
                            workspace
                        )
                    ),
                    workspace_root=(
                        self.__get_workspace_root(
                            workspace
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
                    "SetupPathResolver nÃ£o retornou "
                    "os caminhos do Setup."
                )

            #
            # ========================================================
            # DefiniÃ§Ã£o do Advanced Installer
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
                    "nÃ£o retornou uma definiÃ§Ã£o de Setup."
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
                    "SetupFactory nÃ£o retornou "
                    "um InstallerService."
                )

            #
            # ========================================================
            # ExecuÃ§Ã£o
            # ========================================================
            #

            setup_result = installer.install(
                request=request,
                definition=definition,
                paths=paths,
            )

            setup_message = (
                setup_result.message
                if not setup_result.success
                else "Setup gerado com sucesso."
            )

            setup_result.steps.append(
                StepResult(
                    name="Setup",
                    status=(
                        StepStatus.SUCCESS
                        if setup_result.success
                        else StepStatus.FAILED
                    ),
                    message=setup_message,
                    elapsed_seconds=(
                        setup_result.duration_seconds
                    ),
                    errors=(
                        [setup_result.message]
                        if not setup_result.success
                        else []
                    ),
                )
            )

            return setup_result

        except Exception as exception:

            message = (
                "Erro durante a geração do Setup: "
                f"{exception}"
            )

            return SetupResult(
                success=False,
                message=message,
                project_id=(
                    request.project_id
                ),
                steps=[
                    StepResult(
                        name="Setup",
                        status=StepStatus.FAILED,
                        message=message,
                        errors=[message],
                    ),
                ],
            )

    def __get_engine(
        self,
    ) -> SetupEngine:
        """
        ObtÃ©m o engine configurado.

        Quando AppSettings nÃ£o foi fornecido, utiliza
        Advanced Installer como padrÃ£o.
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
        workspace,
    ) -> Path:
        """
        Obtém a raiz física do projeto.

        A raiz deve ser derivada do arquivo de projeto
        já resolvido pelo WorkspaceResolver.
        """

        return Path(
            workspace.project_file,
        ).parent

    def __get_workspace_root(
        self,
        workspace,
    ) -> Path:
        """
        Obtém a raiz física do ambiente.

        A raiz deve ser a mesma utilizada pelo
        WorkspaceResolver para resolver o projeto.
        """

        return Path(
            workspace.environment.root_path,
        )

    def __get_installer_root(
        self,
    ) -> Path:
        """
        ObtÃ©m a raiz de saÃda dos instaladores.
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
        ObtÃ©m a raiz dos arquivos AIP.
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
