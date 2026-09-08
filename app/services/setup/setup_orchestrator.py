"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_orchestrator.py
DescriÃ§Ã£o : Orquestra o processo de geraÃ§Ã£o do Setup atravÃ©s
            exclusivamente do Advanced Installer.
--------------------------------------------------------------------
"""

from pathlib import Path
from typing import Callable


from app.models.configuration.app_settings import (
    AppSettings,
)

from app.models.execution.pipeline_execution_state import (
    PipelineExecutionPhase,
)

from app.utils.pipeline_logger import (
    PipelineLogger,
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

    PROGRESS_TOTAL_STEPS = 6

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

    @classmethod
    def get_progress_total_steps(
        cls,
        request: SetupRequest,
    ) -> int:
        """
        Retorna a quantidade de etapas de progresso do Setup.
        """

        if request.run_build:
            return cls.PROGRESS_TOTAL_STEPS + 1

        return cls.PROGRESS_TOTAL_STEPS

    @staticmethod
    def __notify_progress(
        progress_callback: Callable[
            [
                str,
                int,
                int,
                int,
                PipelineExecutionPhase,
            ],
            None,
        ] | None,
        step_name: str,
        step_index: int,
        total_steps: int,
        progress_percent: int,
    ) -> None:
        if progress_callback is None:
            return

        progress_callback(
            step_name,
            step_index,
            total_steps,
            progress_percent,
            PipelineExecutionPhase.SETUP,
        )

    def execute(
        self,
        request: SetupRequest,
        progress_callback: Callable[
            [
                str,
                int,
                int,
                int,
                PipelineExecutionPhase,
            ],
            None,
        ] | None = None,
    ) -> SetupResult:
        """
        Executa a geraÃ§Ã£o do Setup.
        """

        if request is None:
            raise ValueError(
                "SetupRequest nÃ£o foi informado."
            )

        try:

            total_steps = self.get_progress_total_steps(
                request,
            )

            PipelineLogger.info(
                "SETUP - INICIO"
            )
            PipelineLogger.info(
                f"Projeto........: {request.project_id}"
            )
            PipelineLogger.info(
                f"Ambiente.......: {request.environment_id}"
            )
            PipelineLogger.info(
                f"Versao.........: {request.version}"
            )
            PipelineLogger.info(
                f"Revisao........: {request.revision}"
            )
            PipelineLogger.info(
                f"Build incluido.: {request.run_build}"
            )
            PipelineLogger.info(
                f"Total de etapas: {total_steps}"
            )

            current_step_index = 1

            #
            # ========================================================
            # Workspace
            # ========================================================
            #

            self.__notify_progress(
                progress_callback,
                "Resolver Workspace",
                current_step_index,
                total_steps,
                int(
                    ((current_step_index - 1) / total_steps) * 100
                ),
            )

            PipelineLogger.info(
                "SETUP - RESOLVENDO WORKSPACE"
            )

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

            PipelineLogger.info(
                f"SETUP - WORKSPACE RESOLVIDO: "
                f"{self.__get_workspace_root(workspace)}"
            )

            current_step_index += 1

            #
            # ========================================================
            # Engine
            # ========================================================
            #

            self.__notify_progress(
                progress_callback,
                "Validar Engine",
                current_step_index,
                total_steps,
                int(
                    ((current_step_index - 1) / total_steps) * 100
                ),
            )

            PipelineLogger.info(
                "SETUP - VALIDANDO ENGINE"
            )

            engine = (
                self.__get_engine()
            )

            PipelineLogger.info(
                f"SETUP - ENGINE: {engine}"
            )

            if engine != SetupEngine.ADVANCED_INSTALLER:
                raise ValueError(
                    "O OuroBuild utiliza exclusivamente "
                    "o Advanced Installer para geraÃ§Ã£o "
                    f"de Setup. Engine configurado: {engine}"
                )

            current_step_index += 1

            #
            # ========================================================
            # Build do projeto
            # ========================================================
            #

            if (
                request.run_build
                and self.__execute_build_use_case is not None
            ):
                self.__notify_progress(
                    progress_callback,
                    "Build",
                    current_step_index,
                    total_steps,
                    int(
                        ((current_step_index - 1) / total_steps) * 100
                    ),
                )

                build_request = BuildRequest(
                    project_id=request.project_id,
                    environment_id=request.environment_id,
                    version=request.version,
                    revision=request.revision,
                )

                PipelineLogger.info(
                    "SETUP - BUILD DO PROJETO - INICIO"
                )

                build_result = (
                    self.__execute_build_use_case.execute(
                        build_request,
                    )
                )

                PipelineLogger.info(
                    f"SETUP - BUILD DO PROJETO - "
                    f"STATUS: {build_result.success}"
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

                    PipelineLogger.error(
                        f"SETUP - BUILD DO PROJETO - FALHA: "
                        f"{message}"
                    )

                    return SetupResult(
                        success=False,
                        message=message,
                        project_id=request.project_id,
                        output_msi=None,
                        duration_seconds=(
                            build_result.elapsed_seconds
                        ),
                        steps=list(
                            build_result.steps
                        ),
                    )

                current_step_index += 1

            # Quando o Build nÃ£o faz parte da execuÃ§Ã£o,
            # a prÃ³xima etapa ocupa a posiÃ§Ã£o atual.
            #
            # ========================================================
            # Caminhos
            # ========================================================
            #

            self.__notify_progress(
                progress_callback,
                "Resolver caminhos",
                current_step_index,
                total_steps,
                int(
                    ((current_step_index - 1) / total_steps) * 100
                ),
            )

            PipelineLogger.info(
                "SETUP - RESOLVENDO CAMINHOS"
            )

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

            PipelineLogger.info(
                f"SETUP - AIP: {paths.aip_path}"
            )
            PipelineLogger.info(
                f"SETUP - OUTPUT MSI: {paths.output_msi}"
            )

            current_step_index += 1

            #
            # ========================================================
            # DefiniÃ§Ã£o do Advanced Installer
            # ========================================================
            #

            self.__notify_progress(
                progress_callback,
                "Carregar definiÃ§Ã£o do Advanced Installer",
                current_step_index,
                total_steps,
                int(
                    ((current_step_index - 1) / total_steps) * 100
                ),
            )

            PipelineLogger.info(
                "SETUP - CARREGANDO DEFINICAO ADVANCED INSTALLER"
            )

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

            PipelineLogger.info(
                "SETUP - DEFINICAO CARREGADA"
            )

            current_step_index += 1

            #
            # ========================================================
            # Installer
            # ========================================================
            #

            self.__notify_progress(
                progress_callback,
                "Criar Installer",
                current_step_index,
                total_steps,
                int(
                    ((current_step_index - 1) / total_steps) * 100
                ),
            )

            PipelineLogger.info(
                "SETUP - CRIANDO INSTALLER"
            )

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

            PipelineLogger.info(
                f"SETUP - INSTALLER: "
                f"{installer.__class__.__name__}"
            )

            current_step_index += 1

            #
            # ========================================================
            # ExecuÃ§Ã£o
            # ========================================================
            #

            self.__notify_progress(
                progress_callback,
                "Executar Setup",
                current_step_index,
                total_steps,
                int(
                    ((current_step_index - 1) / total_steps) * 100
                ),
            )

            PipelineLogger.info(
                "SETUP - EXECUCAO DO ADVANCED INSTALLER - INICIO"
            )

            setup_result = installer.install(
                request=request,
                definition=definition,
                paths=paths,
            )

            PipelineLogger.info(
                f"SETUP - EXECUCAO DO ADVANCED INSTALLER - "
                f"STATUS: {setup_result.success}"
            )

            self.__notify_progress(
                progress_callback,
                "Executar Setup",
                current_step_index,
                total_steps,
                100,
            )

            setup_message = (
                setup_result.message
                if not setup_result.success
                else "Setup gerado com sucesso."
            )

            PipelineLogger.info(
                f"SETUP - RESULTADO: {setup_message}"
            )

            if setup_result.output_msi:
                PipelineLogger.info(
                    f"SETUP - MSI GERADO: "
                    f"{setup_result.output_msi}"
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

            PipelineLogger.info(
                "SETUP - FINAL"
            )

            return setup_result

        except Exception as exception:

            message = (
                "Erro durante a geraÃ§Ã£o do Setup: "
                f"{exception}"
            )

            PipelineLogger.error(
                f"SETUP - FALHA: {message}"
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
        ObtÃ©m a raiz fÃsica do projeto.

        A raiz deve ser derivada do arquivo de projeto
        jÃ¡ resolvido pelo WorkspaceResolver.
        """

        return Path(
            workspace.project_file,
        ).parent

    def __get_workspace_root(
        self,
        workspace,
    ) -> Path:
        """
        ObtÃ©m a raiz fÃsica do ambiente.

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
